"""
Template tags для работы с футером сайта.
"""
from django import template
from home.models import FooterSnippetContact, FooterSnippetCarousel

register = template.Library()


@register.inclusion_tag('blocks/contacts.html', takes_context=True)
def contakts(context):
    """
    Возвращает список контактных данных для футера.
    """
    return {
        'contakts': FooterSnippetContact.objects.all(),
        'request': context['request'],
    }


@register.inclusion_tag('blocks/carusel.html', takes_context=True)
def carusel(context):
    """
    Возвращает список элементов карусели для футера.
    """
    return {
        'carusel': FooterSnippetCarousel.objects.all(),
        'request': context['request'],
    }
