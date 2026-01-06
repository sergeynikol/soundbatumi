"""
Middleware для ограничения доступа к админ-панели только для superuser
"""
from django.shortcuts import redirect
from django.contrib import messages


class AdminAccessMiddleware:
    """
    Middleware для проверки доступа к админ-панели Wagtail.
    Разрешает доступ только для superuser.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Проверяем, является ли запрос к админ-панели Wagtail
        if request.path.startswith('/admin/'):
            # Исключаем статические файлы, медиа и API endpoints
            excluded_paths = [
                '/admin/static/',
                '/admin/media/',
                '/admin/api/',
                '/admin/login/',
                '/admin/logout/',
            ]
            
            # Проверяем, не является ли путь исключенным
            is_excluded = any(request.path.startswith(path) for path in excluded_paths)
            
            if not is_excluded:
                # Проверяем, аутентифицирован ли пользователь
                if not request.user.is_authenticated:
                    # Перенаправляем на страницу входа в админ-панель
                    return redirect('/admin/login/')
                
                # Проверяем, является ли пользователь superuser
                if not request.user.is_superuser:
                    # Для AJAX запросов возвращаем JSON ошибку
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        from django.http import JsonResponse
                        return JsonResponse({
                            'error': 'Доступ к админ-панели разрешен только для администраторов.'
                        }, status=403)
                    
                    # Для обычных запросов показываем сообщение и перенаправляем
                    messages.error(
                        request,
                        'Доступ к админ-панели разрешен только для администраторов.'
                    )
                    return redirect('/')
        
        response = self.get_response(request)
        return response
