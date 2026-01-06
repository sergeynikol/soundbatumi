from django.apps import AppConfig


class HomeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "home"
    
    def ready(self):
        # Регистрируем snippets только если таблицы уже созданы
        # Это предотвращает ошибки при открытии страницы snippets
        try:
            from django.db import connection
            from django.db import OperationalError, ProgrammingError
            
            # Проверяем существование таблиц
            with connection.cursor() as cursor:
                if connection.vendor == 'postgresql':
                    cursor.execute("""
                        SELECT COUNT(*) FROM information_schema.tables 
                        WHERE table_name IN ('home_sitevisit', 'home_visitstatistics', 'home_equipmentdiscountsettings');
                    """)
                    table_count = cursor.fetchone()[0]
                    if table_count >= 2:
                        # Таблицы существуют - регистрируем snippets
                        from wagtail.snippets.models import register_snippet
                        from .models import SiteVisit, VisitStatistics
                        register_snippet(SiteVisit)
                        register_snippet(VisitStatistics)
                        
                        # Регистрируем настройки скидок если таблица существует
                        if table_count >= 3:
                            from .models import EquipmentDiscountSettings
                            register_snippet(EquipmentDiscountSettings)
        except (OperationalError, ProgrammingError):
            # Таблицы не существуют - это нормально, пропускаем регистрацию
            # Сайт будет работать, но snippets не будут доступны до применения миграций
            pass
        except Exception:
            # Другие ошибки тоже игнорируем
            pass
