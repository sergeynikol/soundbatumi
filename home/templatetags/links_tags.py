from django import template
from home.models import UrlFooter, PortnerUrlFuter

register = template.Library()


@register.inclusion_tag('blocks/links_futer.html', takes_context=True)
def links(context):
    return {
        'links': UrlFooter.objects.all(),
        'request': context['request'],
    }


@register.inclusion_tag('blocks/portners.html', takes_context=True)
def portners(context):
    return {
        'portners': PortnerUrlFuter.objects.all(),
        'request': context['request'],
    }
