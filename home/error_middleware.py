"""
Middleware для обработки ошибок базы данных при отсутствии таблиц
"""
from django.db import OperationalError, ProgrammingError
from django.http import Http404


class DatabaseErrorMiddleware:
    """
    Middleware для обработки ошибок базы данных, связанных с отсутствием таблиц.
    Преобразует ошибки в более понятные сообщения.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except (OperationalError, ProgrammingError) as e:
            error_msg = str(e)
            
            # Проверяем, связана ли ошибка с отсутствием таблиц для посещений
            if 'home_sitevisit' in error_msg or 'home_visitstatistics' in error_msg:
                # Если это админ панель, показываем более понятное сообщение
                if '/admin/' in request.path:
                    from django.http import HttpResponse
                    return HttpResponse(
                        f"""
                        <html>
                        <head><title>Таблицы не созданы</title></head>
                        <body style="font-family: Arial; padding: 40px; text-align: center;">
                            <h1>Таблицы для статистики посещений не созданы</h1>
                            <p>Для работы счетчика посещений необходимо выполнить миграции:</p>
                            <pre style="background: #f5f5f5; padding: 20px; display: inline-block; text-align: left;">
python manage.py makemigrations home
python manage.py migrate
                            </pre>
                            <p><a href="/admin/">Вернуться в админ панель</a></p>
                        </body>
                        </html>
                        """,
                        status=503
                    )
            
            # Для других ошибок пробрасываем дальше
            raise
