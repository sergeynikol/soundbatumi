from django import template
from home.models import Footer_snipet_contact, Footer_snipet_carusel

register = template.Library()


@register.inclusion_tag('blocks/contacts.html', takes_context=True)
def contakts(context):
    return {
        'contakts': Footer_snipet_contact.objects.all(),
        'request': context['request'],
    }

@register.inclusion_tag('blocks/carusel.html', takes_context=True)
def carusel(context):
    return {
        'carusel': Footer_snipet_carusel.objects.all(),
        'request': context['request'],
    }
