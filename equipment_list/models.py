from wagtail.admin.panels import FieldPanel
from django.db import models
from wagtail.models import Page
from wagtail.fields import StreamField
from home import blocks


class EquipmentList(Page):
    template = 'equipment_list.html',
    element_equipment = StreamField([
        ('eqipment_cards', blocks.Eqipment_cards())
    ], blank=True, use_json_field=True,)

    diskription_equipment = StreamField([
        ('title_equipments', blocks.DescriptionEquipments())
    ], blank=True, use_json_field=True,)
    promote_keywords = models.TextField(verbose_name="promote_keywords", blank=True, default='')
# поля для ввода данных в интерфейсе администраторa
    content_panels = Page.content_panels + [
        FieldPanel('diskription_equipment'),
        FieldPanel('element_equipment'),    
    ]
    promote_panels = Page.promote_panels + [
        FieldPanel('promote_keywords'),
    ]
