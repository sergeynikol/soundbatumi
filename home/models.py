from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

from wagtail.admin.panels import FieldPanel, FieldRowPanel
from wagtail.models import Page
from wagtail.models import TranslatableMixin 
from wagtail.fields import StreamField
from home import blocks
from wagtail.snippets.models import register_snippet

from django.utils.translation import gettext_lazy as _


class HomePage(Page):
    subpage_types = ['equipment_list.EquipmentList']
    parent_page_types = []
    # поля в базе данных

    banner_slider_settings = StreamField(
        [('banner_slider', blocks.BannerSliderBlock())],
        blank=True,
        use_json_field=True,
        verbose_name=_("Настройки слайдера"),
        max_num=1,
        help_text=_("Настройки для слайдера на главной странице")
    )

    menucards1 = StreamField([('cards_fild', blocks.CardsMenu())],
                              blank=True, 
                              use_json_field=True,
                              verbose_name=_("Карточка меню"))

    promote_keywords = models.TextField(verbose_name=_("Ключевые слова"), blank=True,)

# поля для ввода данных в интерфейсе администраторa
    content_panels = Page.content_panels + [
        FieldPanel('banner_slider_settings'),
        FieldPanel('menucards1'),
    ]

    promote_panels = Page.promote_panels + [
        FieldPanel('promote_keywords'),
    ]

@register_snippet
class Footer_snipet_contact(TranslatableMixin, models.Model):
    url_contact_data = models.URLField(null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    discription = models.CharField(max_length=255, null=True, blank=True)

    panels = [
        FieldPanel('name'),
        FieldPanel('url_contact_data'),
        FieldPanel('phone'),
        FieldPanel('discription'),
    ]

    def __str__(self):
        return str(self.name)

    class Meta(TranslatableMixin.Meta):
        verbose_name = 'контактные данные в фУтере'
        verbose_name_plural = 'контактные данные'


@register_snippet
class UrlFooter(models.Model):
    url_posicion = models.URLField(null=True, blank=True)
    text_link = models.CharField(max_length=255, null=True, blank=True)
    promo_discript = models.CharField(max_length=255, null=True, blank=True)

    panels = [
        FieldPanel('url_posicion'),
        FieldPanel('text_link'),
        FieldPanel('promo_discript'),
    ]

    def __str__(self):
        return str(self.text_link)

    class Meta():
        verbose_name = 'полезная ссылка в футере'
        verbose_name_plural = 'полезные ссылки'


@register_snippet
class PortnerUrlFuter(models.Model):
    url_potner_page = models.URLField(null=True, blank=True)
    text_link_portner = models.CharField(max_length=255, null=True, blank=True)
    promo_discript_portner = models.CharField(max_length=255, null=True, blank=True)

    panels = [
        FieldPanel('url_potner_page'),
        FieldPanel('text_link_portner'),
        FieldPanel('promo_discript_portner'),
    ]

    def __str__(self):
        return str(self.text_link_portner)

    class Meta():
        verbose_name = 'потнера в футере'
        verbose_name_plural = 'Портнеры'


@register_snippet
class Footer_snipet_carusel(models.Model):
    link_band = models.URLField(null=True, blank=True, help_text='ссылка на группу')
    pfoto_in_carusel = models.ImageField(upload_to='carusel/')
    interval = models.IntegerField(null=True, blank=True, help_text='интервал переключения')

    panels = [
        FieldPanel('link_band'),
        FieldPanel('pfoto_in_carusel'),
        FieldPanel('interval'),
    ]

    def __str__(self):
        return str(self.link_band)

    class Meta():
        verbose_name = 'контент карусели в футере'
        verbose_name_plural = 'данные карусели'


# Модель для глобальных настроек скидок на оборудование
# Регистрация как snippet выполняется условно через apps.py
class EquipmentDiscountSettings(models.Model):
    """Глобальные настройки скидок на все оборудование"""
    is_active = models.BooleanField(verbose_name=_('Активировать глобальную скидку'), default=False)
    discount_percent = models.DecimalField(
        verbose_name=_('Процент скидки (%)'),
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text=_('Процент скидки от 0 до 100')
    )
    updated_at = models.DateTimeField(verbose_name=_('Обновлено'), auto_now=True)
    
    class Meta:
        verbose_name = _('Настройки скидок на оборудование')
        verbose_name_plural = _('Настройки скидок на оборудование')
    
    def __str__(self):
        if self.is_active:
            return f"Скидка {self.discount_percent}% активна"
        return "Скидка неактивна"
    
    def save(self, *args, **kwargs):
        # Ограничиваем количество записей до одной
        self.pk = 1
        super().save(*args, **kwargs)
    
    panels = [
        FieldPanel('is_active'),
        FieldPanel('discount_percent'),
    ]
    
    @classmethod
    def get_settings(cls):
        """Получает настройки скидки, создает запись по умолчанию если не существует"""
        obj, created = cls.objects.get_or_create(pk=1, defaults={'is_active': False, 'discount_percent': 0})
        return obj


# Модель для подсчета уникальных посещений
# Регистрация как snippet выполняется условно через apps.py и wagtail_hooks.py
class SiteVisit(models.Model):
    """Модель для хранения уникальных посещений сайта"""
    ip_address = models.GenericIPAddressField(verbose_name=_('IP адрес'))
    user_agent = models.TextField(verbose_name=_('User Agent'), blank=True, null=True)
    visit_date = models.DateField(verbose_name=_('Дата посещения'), default=timezone.now, db_index=True)
    visit_datetime = models.DateTimeField(verbose_name=_('Время посещения'), default=timezone.now, db_index=True)
    path = models.CharField(max_length=255, verbose_name=_('Путь'), blank=True, null=True)
    referer = models.URLField(verbose_name=_('Реферер'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('Посещение')
        verbose_name_plural = _('Посещения')
        ordering = ['-visit_datetime']
        indexes = [
            models.Index(fields=['visit_date', 'ip_address']),
            models.Index(fields=['-visit_datetime']),
        ]
    
    def __str__(self):
        return f"{self.ip_address} - {self.visit_date}"
    
    panels = [
        FieldPanel('ip_address'),
        FieldPanel('user_agent'),
        FieldRowPanel([
            FieldPanel('visit_date'),
            FieldPanel('visit_datetime'),
        ]),
        FieldPanel('path'),
        FieldPanel('referer'),
    ]


# Модель для общей статистики посещений
class VisitStatistics(models.Model):
    """Модель для хранения общей статистики посещений"""
    date = models.DateField(verbose_name=_('Дата'), unique=True, db_index=True)
    unique_visits = models.IntegerField(verbose_name=_('Уникальные посещения'), default=0)
    total_visits = models.IntegerField(verbose_name=_('Всего посещений'), default=0)
    updated_at = models.DateTimeField(verbose_name=_('Обновлено'), auto_now=True)
    
    class Meta:
        verbose_name = _('Статистика посещений')
        verbose_name_plural = _('Статистика посещений')
        ordering = ['-date']
    
    def __str__(self):
        return f"Статистика за {self.date}: {self.unique_visits} уникальных"
    
    panels = [
        FieldPanel('date'),
        FieldRowPanel([
            FieldPanel('unique_visits'),
            FieldPanel('total_visits'),
        ]),
        FieldPanel('updated_at', read_only=True),
    ]


# Модели для заказов
class Order(models.Model):
    """Модель для хранения информации о заказе"""
    STATUS_CHOICES = [
        ('pending', _('Ожидает обработки')),
        ('processing', _('В обработке')),
        ('completed', _('Завершен')),
        ('cancelled', _('Отменен')),
    ]
    
    order_number = models.CharField(
        verbose_name=_('Номер заказа'),
        max_length=50,
        unique=True,
        db_index=True,
        help_text=_('Уникальный номер заказа')
    )
    created_at = models.DateTimeField(
        verbose_name=_('Время создания'),
        auto_now_add=True,
        db_index=True
    )
    delivery_address = models.TextField(
        verbose_name=_('Адрес доставки'),
        help_text=_('Место, куда нужно доставить заказ')
    )
    
    # Связь с пользователем (если заказ оформлен зарегистрированным пользователем)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name=_('Пользователь'),
        help_text=_('Пользователь, оформивший заказ (если зарегистрирован)')
    )
    
    # Контактные данные
    customer_name = models.CharField(
        verbose_name=_('Имя клиента'),
        max_length=255
    )
    customer_phone = models.CharField(
        verbose_name=_('Телефон'),
        max_length=50
    )
    customer_email = models.EmailField(
        verbose_name=_('Email'),
        blank=True,
        null=True
    )
    customer_comment = models.TextField(
        verbose_name=_('Комментарий клиента'),
        blank=True,
        null=True
    )
    
    # Статус и стоимость
    status = models.CharField(
        verbose_name=_('Статус заказа'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    total_amount = models.DecimalField(
        verbose_name=_('Общая сумма заказа'),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    
    class Meta:
        verbose_name = _('Заказ')
        verbose_name_plural = _('Заказы')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['order_number']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Заказ #{self.order_number} от {self.created_at.strftime('%d.%m.%Y %H:%M')}"
    
    def get_total_price(self):
        """Вычисляет общую сумму заказа из позиций"""
        return sum(item.get_total_price() for item in self.items.all())
    
    def get_items_display(self):
        """Возвращает строковое представление позиций заказа для отображения"""
        items = self.items.all()
        if not items:
            return 'Нет позиций'
        return '\n'.join([f"{item.equipment_name} x{item.quantity} - {item.total_price:.2f} ₾" for item in items])
    
    def get_items_count(self):
        """Возвращает количество позиций в заказе"""
        return self.items.count()
    
    def get_equipment_list_short(self):
        """Возвращает полный список оборудования для отображения в таблице"""
        items = self.items.all()
        if not items.exists():
            return '-'
        
        equipment_list = []
        for item in items:
            equipment_list.append(f"{item.equipment_name} (x{item.quantity})")
        
        # Возвращаем все позиции, разделенные переносами строк для отображения в столбик
        return '\n'.join(equipment_list)


class OrderItem(models.Model):
    """Модель для хранения позиций заказа"""
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('Заказ')
    )
    equipment_name = models.CharField(
        verbose_name=_('Наименование оборудования'),
        max_length=255
    )
    equipment_id = models.CharField(
        verbose_name=_('ID оборудования'),
        max_length=255,
        blank=True,
        null=True
    )
    quantity = models.PositiveIntegerField(
        verbose_name=_('Количество'),
        default=1
    )
    unit_price = models.DecimalField(
        verbose_name=_('Цена за единицу'),
        max_digits=10,
        decimal_places=2
    )
    total_price = models.DecimalField(
        verbose_name=_('Общая цена'),
        max_digits=10,
        decimal_places=2
    )
    equipment_image = models.URLField(
        verbose_name=_('Изображение оборудования'),
        blank=True,
        null=True
    )
    
    class Meta:
        verbose_name = _('Позиция заказа')
        verbose_name_plural = _('Позиции заказа')
        ordering = ['id']
    
    def __str__(self):
        return f"{self.equipment_name} x{self.quantity} - {self.total_price} ₾"
    
    def get_total_price(self):
        """Вычисляет общую цену позиции"""
        return self.unit_price * self.quantity
    
    def save(self, *args, **kwargs):
        """Автоматически вычисляет общую цену при сохранении"""
        self.total_price = self.get_total_price()
        super().save(*args, **kwargs)


# Модель профиля пользователя
class UserProfile(models.Model):
    """Расширенный профиль пользователя с дополнительными полями"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name=_('Пользователь')
    )
    phone = models.CharField(
        verbose_name=_('Номер телефона'),
        max_length=50,
        blank=True,
        null=True,
        help_text=_('Номер телефона для связи')
    )
    messenger_link = models.URLField(
        verbose_name=_('Ссылка на мессенджер'),
        blank=True,
        null=True,
        help_text=_('Ссылка на Telegram, WhatsApp или другой мессенджер')
    )
    name_or_organization = models.CharField(
        verbose_name=_('Имя или название организации'),
        max_length=255,
        help_text=_('Ваше имя или название организации')
    )
    created_at = models.DateTimeField(
        verbose_name=_('Дата создания'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        verbose_name=_('Дата обновления'),
        auto_now=True
    )
    
    class Meta:
        verbose_name = _('Профиль пользователя')
        verbose_name_plural = _('Профили пользователей')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Профиль {self.user.username} - {self.name_or_organization}"
    
    def clean(self):
        """Валидация: должно быть указано либо телефон, либо ссылка на мессенджер"""
        from django.core.exceptions import ValidationError
        if not self.phone and not self.messenger_link:
            raise ValidationError(_('Необходимо указать либо номер телефона, либо ссылку на мессенджер.'))
    
    def save(self, *args, **kwargs):
        """Выполняем валидацию перед сохранением"""
        self.full_clean()
        super().save(*args, **kwargs)
