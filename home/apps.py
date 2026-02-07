from django.apps import AppConfig


def _patch_wagtail_localize_extract():
    """
    Патч для wagtail_localize: обрабатываем None в optional полях StreamField.
    Иначе при переводе страницы возникает TypeError: string must be either a
    StringValue or a str. Got NoneType
    """
    try:
        from wagtail_localize.segments import types as segment_types
        from wagtail_localize.segments import extract as segment_extract
        from wagtail_localize.segments import ingest as segment_ingest

        _OriginalStringSegmentValue = segment_types.StringSegmentValue

        class PatchedStringSegmentValue(_OriginalStringSegmentValue):
            def __init__(self, path, string, attrs=None, **kwargs):
                if string is None:
                    string = ""
                super().__init__(path, string, attrs=attrs, **kwargs)

        # Патчим во всех модулях, где используется StringSegmentValue
        segment_types.StringSegmentValue = PatchedStringSegmentValue
        segment_extract.StringSegmentValue = PatchedStringSegmentValue
        segment_ingest.StringSegmentValue = PatchedStringSegmentValue

        # segments.__init__ реэкспортирует из types — обновим и там
        import wagtail_localize.segments as segments_mod
        segments_mod.StringSegmentValue = PatchedStringSegmentValue

        from wagtail_localize.segments.extract import StreamFieldSegmentExtractor

        _original_handle_block = StreamFieldSegmentExtractor.handle_block

        def patched_handle_block(self, block_type, block_value, raw_value=None):
            if block_value is None:
                return []
            return _original_handle_block(self, block_type, block_value, raw_value)

        StreamFieldSegmentExtractor.handle_block = patched_handle_block
    except ImportError:
        pass


class HomeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "home"
    
    def ready(self):
        _patch_wagtail_localize_extract()

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
