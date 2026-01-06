"""
Middleware для подсчета уникальных посещений сайта
"""
import hashlib
from django.utils import timezone
from django.core.cache import cache
from django.db import OperationalError, ProgrammingError
from home.models import SiteVisit, VisitStatistics


class VisitCounterMiddleware:
    """
    Middleware для подсчета уникальных посещений.
    Использует комбинацию IP адреса и даты для определения уникальности.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Пропускаем статические файлы и админ панель
        path = request.path
        
        if self._should_skip_path(path):
            return self.get_response(request)
        
        # Проверяем, существуют ли таблицы - если нет, просто пропускаем подсчет
        # Это нормально при первом запуске, пока не применены миграции
        
        # Получаем IP адрес
        ip_address = self._get_client_ip(request)
        
        # Получаем текущую дату
        today = timezone.now().date()
        
        # Получаем User-Agent (обрезаем до 200 символов для уникальности)
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:200]
        
        # Создаем ключ для кеша (IP + дата + хеш user agent)
        cache_key = f"visit_{ip_address}_{today}_{hashlib.md5(user_agent.encode()).hexdigest()[:10]}"
        
        # Проверяем, не был ли этот визит уже засчитан сегодня
        if not cache.get(cache_key):
            try:
                # Проверяем, существует ли запись в БД
                # Если таблицы не существуют, это вызовет OperationalError, который мы поймаем
                visit_exists = SiteVisit.objects.filter(
                    ip_address=ip_address,
                    visit_date=today,
                    user_agent=user_agent
                ).exists()
                
                if not visit_exists:
                    # Создаем новую запись о посещении
                    SiteVisit.objects.create(
                        ip_address=ip_address,
                        user_agent=user_agent,
                        visit_date=today,
                        visit_datetime=timezone.now(),
                        path=path[:255],
                        referer=request.META.get('HTTP_REFERER', '')[:200] or None
                    )
                    
                    # Обновляем статистику за сегодня
                    stats, created = VisitStatistics.objects.get_or_create(
                        date=today,
                        defaults={'unique_visits': 0, 'total_visits': 0}
                    )
                    stats.unique_visits += 1
                    stats.total_visits += 1
                    stats.save()
                    
                    # Сохраняем в кеш на 24 часа
                    cache.set(cache_key, True, 86400)  # 24 часа
                else:
                    # Обновляем только общее количество посещений
                    stats, created = VisitStatistics.objects.get_or_create(
                        date=today,
                        defaults={'unique_visits': 0, 'total_visits': 0}
                    )
                    stats.total_visits += 1
                    stats.save()
                    
                    # Сохраняем в кеш на 24 часа
                    cache.set(cache_key, True, 86400)
            except (OperationalError, ProgrammingError) as e:
                # Таблицы не существуют (миграции еще не применены) - это нормально
                # Просто пропускаем подсчет посещений
                import logging
                logger = logging.getLogger(__name__)
                logger.debug(f"VisitCounterMiddleware: tables not created yet: {e}")
            except Exception as e:
                # Другие ошибки логируем, но не прерываем обработку запроса
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error in VisitCounterMiddleware: {e}")
        
        return self.get_response(request)
    
    def _get_client_ip(self, request):
        """Получает IP адрес клиента"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _should_skip_path(self, path):
        """Определяет, нужно ли пропустить этот путь"""
        skip_paths = [
            '/static/',
            '/media/',
            '/admin/',
            '/django-admin/',
            '/favicon.ico',
            '/robots.txt',
            '/sitemap.xml',
        ]
        return any(path.startswith(skip) for skip in skip_paths)
