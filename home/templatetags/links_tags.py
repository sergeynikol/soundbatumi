"""
Template tags для работы со ссылками и партнерами в футере.
"""
from django import template
from home.models import UrlFooter, PartnerUrlFooter

register = template.Library()


@register.inclusion_tag('blocks/links_futer.html', takes_context=True)
def links(context):
    """
    Возвращает список полезных ссылок для футера.
    """
    return {
        'links': UrlFooter.objects.all(),
        'request': context['request'],
    }


@register.inclusion_tag('blocks/portners.html', takes_context=True)
def portners(context):
    """
    Возвращает список партнеров для футера.
    """
    return {
        'portners': PartnerUrlFooter.objects.all(),
        'request': context['request'],
    }
