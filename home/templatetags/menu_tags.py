from django import template
import re
# from home.models import Menu_Snipet
from wagtail.models import Site, Locale, Page

register = template.Library()


@register.simple_tag(takes_context=True)
def get_site_root(context):
    return Site.find_for_request(context['request']).root_page


@register.simple_tag(takes_context=True)
def get_page_translation(context, page, language_code):
    """
    Получает локализованную версию страницы для указанного языка.
    Если перевод не найден, возвращает None.
    """
    if not page:
        return None

    try:
        # Получаем locale по языковому коду
        locale = Locale.objects.get(language_code=language_code)
        # Получаем все переводы страницы
        translations = (
            page.get_translations(inclusive=True)
            .filter(locale=locale)
            .live()
        )
        if translations.exists():
            return translations.first()
    except Locale.DoesNotExist:
        pass

    return None


@register.simple_tag
def extract_page_from_richtext(richtext):
    """
    Извлекает объект страницы из RichText блока.
    Ищет ссылку типа <a id="9" linktype="page"> в RichText.
    """
    if not richtext:
        return None

    # Преобразуем RichText в строку
    text = str(richtext)

    # Ищем id страницы в ссылке - несколько вариантов паттернов
    patterns = [
        # Стандартный формат Wagtail: <a id="9" linktype="page">
        r'<a[^>]+id=["\'](\d+)["\'][^>]*linktype=["\']page["\']',
        # Альтернативный формат: <a linktype="page" id="9">
        r'<a[^>]+linktype=["\']page["\'][^>]*id=["\'](\d+)["\']',
        # Формат с data-linktype
        r'<a[^>]+data-linktype=["\']page["\'][^>]*id=["\'](\d+)["\']',
        r'<a[^>]+id=["\'](\d+)["\'][^>]*data-linktype=["\']page["\']',
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            page_id = int(match.group(1))
            try:
                page = Page.objects.get(id=page_id).specific
                # Проверяем, что страница опубликована
                if page.live:
                    return page
            except (Page.DoesNotExist, AttributeError, ValueError):
                continue

    return None


@register.inclusion_tag('blocks/menu.html', takes_context=True)
def menus(context, parent):
    menuitems = parent.get_children().live().in_menu()
    # Получаем текущую страницу из контекста, если она есть
    current_page = context.get('page', None)
    # Получаем пользователя из контекста (добавляется context_processors.auth)
    user = context.get('user', None)
    return {
        'menuitems': menuitems,
        'request': context['request'],
        'current_page': current_page,
        'user': user,  # Передаем пользователя в шаблон меню
    }


@register.simple_tag(takes_context=True)
def get_menu_items(context):
    """
    Получает список пунктов меню для использования в шаблонах карточек.
    Возвращает список страниц, которые отображаются в меню.
    """
    try:
        request = context.get('request')
        if request:
            site = Site.find_for_request(request)
            if site and site.root_page:
                menuitems = site.root_page.get_children().live().in_menu()
                return list(menuitems)
    except Exception:
        pass
    return []


@register.simple_tag(takes_context=True)
def find_menu_page_by_text(context, text):
    """
    Находит страницу в меню по тексту из RichText поля карточки.
    Сопоставляет текст карточки с названиями пунктов меню.
    """
    if not text:
        return None
    
    try:
        # Очищаем текст от HTML тегов
        import re
        clean_text = re.sub(r'<[^>]+>', '', str(text)).strip()
        
        # Если текст пустой после очистки, возвращаем None
        if not clean_text:
            return None
        
        request = context.get('request')
        if request:
            site = Site.find_for_request(request)
            if site and site.root_page:
                menuitems = site.root_page.get_children().live().in_menu()
                
                # Ищем страницу по точному совпадению названия (без учета регистра)
                for item in menuitems:
                    # Проверяем локализованную версию
                    if hasattr(item, 'localized') and item.localized:
                        localized = item.localized
                        if localized.title.lower().strip() == clean_text.lower().strip():
                            return localized
                    
                    # Проверяем оригинальное название
                    if item.title.lower().strip() == clean_text.lower().strip():
                        return item
                
                # Если точного совпадения нет, ищем частичное совпадение
                for item in menuitems:
                    if hasattr(item, 'localized') and item.localized:
                        localized = item.localized
                        # Проверяем, содержит ли название карточки название страницы или наоборот
                        if (clean_text.lower().strip() in localized.title.lower().strip() or 
                            localized.title.lower().strip() in clean_text.lower().strip()):
                            return localized
                    
                    if (clean_text.lower().strip() in item.title.lower().strip() or 
                        item.title.lower().strip() in clean_text.lower().strip()):
                        return item
    except Exception:
        pass
    
    return None
