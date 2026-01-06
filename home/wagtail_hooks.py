"""
Wagtail hooks для добавления статистики посещений на главную страницу админ панели
"""
from wagtail import hooks
from django.utils.html import format_html
from django.db.models import Sum
from django.db import OperationalError, ProgrammingError
from django.utils import timezone
from datetime import timedelta

# Импортируем ViewSet для заказов
try:
    from .wagtail_admin import order_viewset
except (ImportError, Exception):
    order_viewset = None


@hooks.register('construct_snippet_listing_queryset')
def filter_snippet_queryset(model, queryset, request):
    """Фильтрует queryset для snippets, если таблицы не существуют"""
    try:
        model_name = model._meta.db_table if hasattr(model, '_meta') else None
        
        if model_name in ['home_sitevisit', 'home_visitstatistics']:
            # Проверяем существование таблицы через попытку выполнения запроса
            try:
                # Пробуем выполнить простой запрос - если таблица не существует, будет ошибка
                list(queryset[:1])
            except (OperationalError, ProgrammingError):
                # Таблица не существует - возвращаем пустой queryset
                return queryset.none()
    except (AttributeError, Exception):
        # Если не удалось определить модель, возвращаем queryset как есть
        pass
    
    return queryset


@hooks.register('construct_homepage_panels')
def add_visit_statistics_panel(request, panels):
    """Добавляет панель со статистикой посещений на главную страницу админ панели"""
    from wagtail.admin.panels import Panel
    
    # Пробуем получить статистику, если таблицы не существуют - просто пропускаем
    try:
        # Импортируем модели только здесь, чтобы избежать ошибок при загрузке модуля
        from .models import SiteVisit, VisitStatistics
        
        # Получаем статистику
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        # Статистика за сегодня
        today_stats = VisitStatistics.objects.filter(date=today).first()
        today_unique = today_stats.unique_visits if today_stats else 0
        today_total = today_stats.total_visits if today_stats else 0
        
        # Статистика за вчера
        yesterday_stats = VisitStatistics.objects.filter(date=yesterday).first()
        yesterday_unique = yesterday_stats.unique_visits if yesterday_stats else 0
        
        # Статистика за последние 7 дней
        week_ago = today - timedelta(days=7)
        week_stats = VisitStatistics.objects.filter(date__gte=week_ago).aggregate(
            total_unique=Sum('unique_visits'),
            total_visits=Sum('total_visits')
        )
        week_unique = week_stats['total_unique'] or 0
        week_total = week_stats['total_visits'] or 0
        
        # Статистика за все время
        all_time_stats = VisitStatistics.objects.aggregate(
            total_unique=Sum('unique_visits'),
            total_visits=Sum('total_visits')
        )
        all_time_unique = all_time_stats['total_unique'] or 0
        all_time_total = all_time_stats['total_visits'] or 0
        
        # Всего уникальных посетителей (по IP)
        total_unique_ips = SiteVisit.objects.values('ip_address').distinct().count()
        
        # Добавляем панель со статистикой
        panels.append(
            Panel(
                heading='Статистика посещений',
                content=format_html(
                    '''
                    <div style="padding: 20px;">
                        <h3 style="margin-top: 0;">Статистика посещений сайта</h3>
                        <table style="width: 100%; margin-top: 15px; border-collapse: collapse;">
                            <tr style="background: #f8f9fa; border-bottom: 2px solid #dee2e6;">
                                <td style="padding: 10px; font-weight: bold;">Период</td>
                                <td style="padding: 10px; font-weight: bold; text-align: right;">Уникальные</td>
                                <td style="padding: 10px; font-weight: bold; text-align: right;">Всего</td>
                            </tr>
                            <tr>
                                <td style="padding: 10px; border-bottom: 1px solid #dee2e6;">Сегодня</td>
                                <td style="padding: 10px; text-align: right; border-bottom: 1px solid #dee2e6;"><strong style="color: #2487ce;">{}</strong></td>
                                <td style="padding: 10px; text-align: right; border-bottom: 1px solid #dee2e6;">{}</td>
                            </tr>
                            <tr>
                                <td style="padding: 10px; border-bottom: 1px solid #dee2e6;">Вчера</td>
                                <td style="padding: 10px; text-align: right; border-bottom: 1px solid #dee2e6;">{}</td>
                                <td style="padding: 10px; text-align: right; border-bottom: 1px solid #dee2e6;">-</td>
                            </tr>
                            <tr>
                                <td style="padding: 10px; border-bottom: 1px solid #dee2e6;">Последние 7 дней</td>
                                <td style="padding: 10px; text-align: right; border-bottom: 1px solid #dee2e6;"><strong style="color: #2487ce;">{}</strong></td>
                                <td style="padding: 10px; text-align: right; border-bottom: 1px solid #dee2e6;">{}</td>
                            </tr>
                            <tr style="background: #e9ecef;">
                                <td style="padding: 10px; font-weight: bold;">Всего</td>
                                <td style="padding: 10px; text-align: right; font-weight: bold; color: #2487ce;">{}</td>
                                <td style="padding: 10px; text-align: right; font-weight: bold;">{}</td>
                            </tr>
                        </table>
                        <p style="margin-top: 15px; margin-bottom: 10px; color: #6c757d; font-size: 14px;">
                            Всего уникальных IP адресов: <strong>{}</strong>
                        </p>
                        <div style="margin-top: 20px;">
                            <a href="/admin/snippets/home/visitstatistics/" 
                               class="button button-secondary" 
                               style="margin-right: 10px;">Подробная статистика</a>
                            <a href="/admin/snippets/home/sitevisit/" 
                               class="button button-secondary">История посещений</a>
                        </div>
                    </div>
                    ''',
                    today_unique, today_total,
                    yesterday_unique,
                    week_unique, week_total,
                    all_time_unique, all_time_total,
                    total_unique_ips
                )
            )
        )
        
    except (OperationalError, ProgrammingError) as e:
        # Таблицы не существуют (миграции еще не применены) - это нормально
        # Просто пропускаем добавление панели
        pass
    except Exception as e:
        # Другие ошибки логируем, но не прерываем работу админ панели
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Could not load visit statistics: {e}")
    
    # Добавляем панель со ссылкой на заказы в той же функции
    try:
        panels.append(
            Panel(
                heading='Управление заказами',
                content=format_html(
                    '''
                    <div style="padding: 20px;">
                        <p style="margin-bottom: 15px;">Просмотр и управление заказами клиентов.</p>
                        <div style="margin-top: 15px;">
                            <a href="/admin/order/" 
                               class="button button-primary" 
                               style="text-decoration: none; display: inline-block; padding: 10px 20px; background-color: #2487ce; color: white; border-radius: 4px; font-weight: bold;">
                                Перейти к заказам
                            </a>
                        </div>
                    </div>
                    '''
                )
            )
        )
    except Exception as e:
        # Игнорируем ошибки, чтобы не нарушить работу админ панели
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Could not load orders panel: {e}")
    
    return panels


@hooks.register("register_admin_viewset")
def register_order_viewset():
    """Регистрируем ViewSet для заказов"""
    if order_viewset is not None:
        return order_viewset


@hooks.register("register_admin_menu_item")
def register_orders_menu_item():
    """Добавляем кнопку заказов в меню админ-панели"""
    from wagtail.admin.menu import MenuItem
    
    return MenuItem(
        'Заказы',
        '/admin/order/',
        icon_name='list-ul',
        order=200
    )


