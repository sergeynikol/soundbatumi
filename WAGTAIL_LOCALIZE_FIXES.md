# Исправления проблем с wagtail_localize

## ⚠️ КРИТИЧЕСКАЯ ОШИБКА: column "page_revision_id" does not exist

Если вы получили ошибку:
```
ProgrammingError: column "page_revision_id" of relation "wagtail_localize_translationlog" does not exist
```

**Быстрое решение:**
```bash
cd /home/serg/pythonlerning/sites/code/soundbatumi
python fix_translationlog.py
```

Или через Django shell:
```bash
python manage.py shell < fix_translationlog.py
```

Подробные инструкции см. в файле `fix_wagtail_localize.md`

---

## Исправленные проблемы

### 1. Несоответствие LANGUAGE_CODE и WAGTAIL_CONTENT_LANGUAGES
**Проблема:** `LANGUAGE_CODE` был установлен в `"en-us"`, а первый язык в `WAGTAIL_CONTENT_LANGUAGES` - `'en'`. Это несоответствие может вызывать проблемы с wagtail_localize.

**Исправление:** Изменен `LANGUAGE_CODE` с `"en-us"` на `"en"` в файле `soundbatumi/settings/base.py`.

### 2. Оптимизация URL паттернов
**Проблема:** Некоторые URL были дублированы, а некоторые должны быть доступны без языкового префикса (например, API endpoints).

**Исправление:** 
- API endpoints (`/api/create-order/`, `/api/telegram-login/`, и т.д.) вынесены из `i18n_patterns` - они доступны без языкового префикса
- Страницы входа/регистрации перемещены в `i18n_patterns` для поддержки локализации
- Добавлен параметр `prefix_default_language=False` в `i18n_patterns` - язык по умолчанию (en) не будет иметь префикса в URL

## Что нужно проверить и настроить

### 1. Создание локалей в базе данных
После применения исправлений необходимо создать локали в админ-панели Wagtail:

1. Войдите в админ-панель Wagtail: `/admin/`
2. Перейдите в **Settings → Locales**
3. Убедитесь, что созданы локали для всех языков:
   - English (en) - должен быть установлен как язык по умолчанию
   - Georgian (ka)
   - Russian (ru)

Если локали не созданы, создайте их вручную.

### 2. Применение миграций
Убедитесь, что все миграции применены:

```bash
python manage.py migrate
```

Если есть новые миграции для wagtail_localize:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Проверка моделей
Убедитесь, что модели правильно настроены для перевода:

- **HomePage** - наследуется от `Page`, автоматически поддерживает переводы
- **EquipmentList** - наследуется от `Page`, автоматически поддерживает переводы
- **FooterSnippetContact** - использует `TranslatableMixin`, правильно настроен

### 4. Создание переводов страниц
После настройки локалей:

1. Создайте или откройте страницу в админ-панели
2. В меню страницы должна появиться опция "Translate" или "Создать перевод"
3. Создайте переводы для каждого языка

## Дополнительные настройки (опционально)

### Настройка полей для перевода
Если нужно настроить, какие поля переводятся, а какие синхронизируются, можно использовать `override_translatable_fields` в моделях:

```python
from wagtail_localize.models import TranslationComponent

@register_translation_component
class HomePageTranslationComponent(TranslationComponent):
    model = HomePage
    
    override_translatable_fields = [
        'title',
        'banner_slider_settings',
        'menucards1',
    ]
```

Однако, для большинства случаев автоматическое определение полей работает хорошо.

## Проверка работоспособности

1. **Проверьте админ-панель:**
   - Убедитесь, что в админ-панели нет ошибок
   - Проверьте, что локали отображаются в Settings → Locales

2. **Проверьте создание переводов:**
   - Откройте любую страницу
   - Попробуйте создать перевод для другого языка

3. **Проверьте фронтенд:**
   - Убедитесь, что страницы доступны на разных языках
   - Проверьте переключение языков

## Возможные проблемы и решения

### Проблема: Локали не создаются автоматически
**Решение:** Создайте их вручную через админ-панель Settings → Locales

### Проблема: Переводы не синхронизируются
**Решение:** 
- Убедитесь, что `WAGTAIL_I18N_ENABLED = True`
- Проверьте, что локали правильно настроены
- Используйте команду синхронизации: `python manage.py sync_page_translation_fields`

### Проблема: Ошибки при создании переводов
**Решение:**
- Проверьте логи Django на наличие ошибок
- Убедитесь, что все миграции применены
- Проверьте, что модели правильно наследуются от `Page` или используют `TranslatableMixin`

## Полезные команды

```bash
# Применить миграции
python manage.py migrate

# Создать новые миграции
python manage.py makemigrations

# Синхронизировать поля переводов
python manage.py sync_page_translation_fields

# Проверить конфигурацию
python manage.py check
```

## Документация

- [Wagtail Localize Documentation](https://wagtail-localize.org/)
- [Wagtail i18n Documentation](https://docs.wagtail.org/en/stable/advanced_topics/i18n.html)
