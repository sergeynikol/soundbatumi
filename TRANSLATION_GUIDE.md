# Руководство по переводам / Translation Guide

## Что было сделано / What was done

### 1. HTML Шаблоны / HTML Templates

Все текстовые строки в HTML шаблонах были обернуты в теги `{% trans %}` для поддержки многоязычности:

- `soundbatumi/templates/blocks/menucards.html` - добавлены переводы для "Подробнее" и "Перейти на страницу"
- `soundbatumi/templates/blocks/equipment_photo_modal.html` - добавлены переводы для "Фото товара"
- `soundbatumi/templates/blocks/banner_slider_block.html` - **НОВОЕ!** добавлены переводы для всех кнопок и текстов слайдера:
  - "Узнать больше" → "Learn more"
  - "You can be yourself"
  - "About Us"
  - "Professional Equipment"
  - "Choose us once, and you will choose us always"
  - "Our Equipment"
  - "Contact Us"
  - "Where friends and family will always feel at home!"
- `soundbatumi/templates/blocks/listeq.html` - **НОВОЕ!** добавлен перевод для "SALE"
- `soundbatumi/templates/base.html` - обновлены комментарии с переводами

### 2. JavaScript (main.js)

Все жестко закодированные русские строки в `main.js` теперь используют `window.TRANSLATIONS`:

```javascript
const t = window.TRANSLATIONS || {};
console.log(t.image_loaded || 'Image loaded:', url);
```

### 3. Переводы в base.html

В `base.html` добавлены все необходимые переводы для JavaScript в объекте `window.TRANSLATIONS`:

```html
<script>
  window.LANGUAGE_CODE = '{{ LANGUAGE_CODE }}';
  window.TRANSLATIONS = {
    'learn_more': '{% trans "Learn more" %}',
    'go_to_page': '{% trans "Go to page" %}',
    'product_photo': '{% trans "Product Photo" %}',
    // ... и многие другие
  };
</script>
```

### 4. Файлы переводов (.po)

Переводы добавлены для всех трех языков:

- **English (en)**: `/locale/en/LC_MESSAGES/django.po`
- **Russian (ru)**: `/locale/ru/LC_MESSAGES/django.po`
- **Georgian (ka)**: `/locale/ka/LC_MESSAGES/django.po`

### 5. Скомпилированные переводы (.mo)

Все переводы скомпилированы и готовы к использованию.

## Как добавить новые переводы / How to add new translations

### Шаг 1: Добавьте теги перевода в HTML / Step 1: Add translation tags in HTML

```html
<!-- Плохо / Bad -->
<h1>Привет мир</h1>

<!-- Хорошо / Good -->
{% load i18n %}
<h1>{% trans "Hello world" %}</h1>
```

### Шаг 2: Используйте window.TRANSLATIONS в JavaScript / Step 2: Use window.TRANSLATIONS in JavaScript

```javascript
// Плохо / Bad
console.log('Ошибка загрузки');

// Хорошо / Good
const t = window.TRANSLATIONS || {};
console.log(t.loading_error || 'Loading error');
```

И добавьте в `base.html`:

```html
<script>
  window.TRANSLATIONS = {
    ...
    'loading_error': '{% trans "Loading error" %}',
    ...
  };
</script>
```

### Шаг 3: Извлеките новые строки / Step 3: Extract new strings

```bash
cd /home/serg/pythonlerning/sites/code/soundbatumi
source ../.venv/bin/activate
python manage.py makemessages -l en --ignore=.venv
python manage.py makemessages -l ru --ignore=.venv
python manage.py makemessages -l ka --ignore=.venv
```

### Шаг 4: Добавьте переводы в .po файлы / Step 4: Add translations to .po files

Откройте файлы в `locale/<lang>/LC_MESSAGES/django.po` и заполните `msgstr`:

```
msgid "Hello world"
msgstr "Привет мир"  # для ru
msgstr "გამარჯობა მსოფლიო"  # для ka
msgstr "Hello world"  # для en (то же самое)
```

### Шаг 5: Скомпилируйте переводы / Step 5: Compile translations

```bash
python manage.py compilemessages
```

### Шаг 6: Перезапустите сервер / Step 6: Restart the server

```bash
python manage.py runserver
```

## Структура переводов / Translation structure

```
soundbatumi/
├── locale/
│   ├── en/
│   │   └── LC_MESSAGES/
│   │       ├── django.po  # Исходные переводы (редактируйте)
│   │       └── django.mo  # Скомпилированные (не редактируйте)
│   ├── ru/
│   │   └── LC_MESSAGES/
│   │       ├── django.po
│   │       └── django.mo
│   └── ka/
│       └── LC_MESSAGES/
│           ├── django.po
│           └── django.mo
└── templates/
    └── base.html  # window.TRANSLATIONS для JavaScript
```

## Поддерживаемые языки / Supported languages

1. **English (en)** - Английский
2. **Russian (ru)** - Русский
3. **Georgian (ka)** - Грузинский (ქართული)

## Переключение языков / Language switching

Пользователи могут переключать языки через выпадающее меню в навигации (иконка с флагом).

Переключение языка изменяет:
- Все тексты в HTML шаблонах
- Все тексты в JavaScript через `window.TRANSLATIONS`
- URL страниц (например, `/en/`, `/ru/`, `/ka/`)

## Важные замечания / Important notes

1. **Всегда используйте {% trans %}** для всех видимых пользователю текстов
2. **Никогда не жестко кодируйте текст** на одном языке
3. **Всегда компилируйте переводы** после изменений
4. **Тестируйте на всех языках** перед деплоем
5. **Используйте короткие ключи** для `window.TRANSLATIONS` (например, `cart_empty` вместо `cart_is_empty_message_text`)

## Полезные команды / Useful commands

```bash
# Извлечь все строки для перевода
python manage.py makemessages -a --ignore=.venv

# Извлечь строки для конкретного языка
python manage.py makemessages -l ru --ignore=.venv

# Скомпилировать все переводы
python manage.py compilemessages

# Проверить текущий язык
python manage.py shell
>>> from django.utils.translation import get_language
>>> get_language()
```

## Troubleshooting

### Переводы не отображаются / Translations not showing

1. Проверьте, что переводы скомпилированы: `python manage.py compilemessages`
2. Перезапустите сервер
3. Очистите кэш браузера
4. Проверьте, что в настройках `USE_I18N = True`

### JavaScript не использует переводы / JavaScript not using translations

1. Убедитесь, что `window.TRANSLATIONS` определен в `base.html`
2. Проверьте консоль браузера на наличие ошибок
3. Убедитесь, что ключ существует в `window.TRANSLATIONS`

### Грузинский текст отображается некорректно / Georgian text displays incorrectly

1. Убедитесь, что файл `.po` сохранен в UTF-8
2. Проверьте, что в базе данных используется UTF-8
3. Убедитесь, что шрифты поддерживают грузинские символы

## Контрибьюция / Contributing

При добавлении новых функций:
1. Всегда используйте переводы для новых текстов
2. Добавляйте переводы для всех трех языков
3. Тестируйте на всех языках
4. Документируйте новые ключи переводов

---

**Автор / Author**: SERGO_NIK  
**Дата / Date**: 2026-01-21  
**Версия / Version**: 1.0
