from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html, escape
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils import timezone
from django.contrib import messages
from datetime import timedelta
from .models import Order, OrderItem, UserProfile


class ObsoleteOrdersFilter(admin.SimpleListFilter):
    """Фильтр для отображения неактуальных заказов"""
    title = 'Тип заказов'
    parameter_name = 'order_type'
    
    def lookups(self, request, model_admin):
        return (
            ('obsolete', 'Неактуальные (завершенные/отмененные)'),
            ('old_completed', 'Старые завершенные (старше 6 мес.)'),
            ('old_cancelled', 'Старые отмененные (старше 3 мес.)'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'obsolete':
            return queryset.filter(status__in=['completed', 'cancelled'])
        elif self.value() == 'old_completed':
            six_months_ago = timezone.now() - timedelta(days=180)
            return queryset.filter(status='completed', created_at__lt=six_months_ago)
        elif self.value() == 'old_cancelled':
            three_months_ago = timezone.now() - timedelta(days=90)
            return queryset.filter(status='cancelled', created_at__lt=three_months_ago)
        return queryset


class OrderItemInline(admin.TabularInline):
    """Инлайн для отображения позиций заказа в админке"""
    model = OrderItem
    extra = 0
    readonly_fields = ('equipment_name', 'quantity', 'unit_price', 'total_price', 'equipment_image_preview')
    fields = ('equipment_name', 'quantity', 'unit_price', 'total_price', 'equipment_image_preview')
    can_delete = False
    
    def equipment_image_preview(self, obj):
        """Отображение миниатюры изображения оборудования"""
        if obj.equipment_image:
            return format_html(
                '<img src="{}" style="max-width: 50px; max-height: 50px;" />',
                obj.equipment_image
            )
        return '-'
    equipment_image_preview.short_description = 'Изображение'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Админ-панель для управления заказами"""
    list_display = (
        'order_number_link',
        'created_at',
        'customer_name',
        'customer_phone',
        'delivery_address_short',
        'installation_datetime_display',
        'equipment_list_display',
        'status',
        'total_amount_display',
        'items_count'
    )
    list_filter = ('status', 'created_at', 'installation_date', ObsoleteOrdersFilter)
    search_fields = ('order_number', 'customer_name', 'customer_phone', 'customer_email')
    readonly_fields = (
        'order_number',
        'created_at',
        'total_amount',
        'items_list',
        'contact_info'
    )
    fieldsets = (
        ('Основная информация', {
            'fields': ('order_number', 'created_at', 'status')
        }),
        ('Контактные данные', {
            'fields': ('contact_info', 'customer_name', 'customer_phone', 'customer_email', 'customer_comment')
        }),
        ('Доставка и монтаж', {
            'fields': ('delivery_address', 'installation_date', 'installation_time')
        }),
        ('Состав заказа', {
            'fields': ('items_list', 'total_amount')
        }),
    )
    inlines = [OrderItemInline]
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        """Оптимизация запросов - предзагрузка связанных объектов"""
        queryset = super().get_queryset(request)
        return queryset.prefetch_related('items')
    
    def order_number_link(self, obj):
        """Ссылка на детальную страницу заказа"""
        url = reverse('admin:home_order_change', args=[obj.pk])
        return format_html('<a href="{}">{}</a>', url, obj.order_number)
    order_number_link.short_description = 'Номер заказа'
    
    def delivery_address_short(self, obj):
        """Короткий адрес доставки для списка"""
        if len(obj.delivery_address) > 50:
            return obj.delivery_address[:50] + '...'
        return obj.delivery_address
    delivery_address_short.short_description = 'Адрес доставки'
    
    def total_amount_display(self, obj):
        """Отображение общей суммы с форматированием"""
        return f"{obj.total_amount:.2f} ₾"
    total_amount_display.short_description = 'Общая сумма'
    
    def items_count(self, obj):
        """Количество позиций в заказе"""
        return obj.items.count()
    items_count.short_description = 'Позиций'
    
    def installation_datetime_display(self, obj):
        """Отображение даты и времени монтажа"""
        if obj.installation_date:
            date_str = obj.installation_date.strftime('%d.%m.%Y')
            if obj.installation_time:
                time_str = obj.installation_time.strftime('%H:%M')
                return f"{date_str} {time_str}"
            return date_str
        return format_html('<span style="color: #999;">-</span>')
    installation_datetime_display.short_description = 'Дата/время монтажа'
    
    def equipment_list_display(self, obj):
        """Отображение списка заказанного оборудования в таблице"""
        try:
            # Используем prefetch_related для оптимизации
            items = list(obj.items.all())
            if not items:
                return format_html('<span style="color: #999;">-</span>')
            
            # Формируем список оборудования с количеством - выводим все позиции
            equipment_list = []
            for item in items:
                equipment_list.append(f"{item.equipment_name} (x{item.quantity})")
            
            # Объединяем в строку с переносами для отображения в столбик
            result_html = '<br>'.join([escape(item) for item in equipment_list])
            
            return format_html(
                '<div style="max-width: 300px; word-wrap: break-word; font-size: 12px; line-height: 1.5;">{}</div>',
                mark_safe(result_html)
            )
        except Exception as e:
            return format_html('<span style="color: red;">Ошибка: {}</span>', str(e))
    equipment_list_display.short_description = 'Заказанное оборудование'
    
    def items_list(self, obj):
        """Таблица со списком позиций заказа"""
        items = obj.items.all()
        if not items:
            return 'Нет позиций'
        
        html = '<table style="width: 100%; border-collapse: collapse; margin-top: 10px;">'
        html += '<thead><tr style="background-color: #f5f5f5;">'
        html += '<th style="padding: 8px; border: 1px solid #ddd; text-align: left;">Наименование</th>'
        html += '<th style="padding: 8px; border: 1px solid #ddd; text-align: center;">Количество</th>'
        html += '<th style="padding: 8px; border: 1px solid #ddd; text-align: right;">Цена за единицу</th>'
        html += '<th style="padding: 8px; border: 1px solid #ddd; text-align: right;">Общая цена</th>'
        html += '</tr></thead><tbody>'
        
        for item in items:
            html += '<tr>'
            html += f'<td style="padding: 8px; border: 1px solid #ddd;">{escape(item.equipment_name)}</td>'
            html += f'<td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{item.quantity}</td>'
            html += f'<td style="padding: 8px; border: 1px solid #ddd; text-align: right;">{item.unit_price:.2f} ₾</td>'
            html += f'<td style="padding: 8px; border: 1px solid #ddd; text-align: right;">{item.total_price:.2f} ₾</td>'
            html += '</tr>'
        
        html += '</tbody></table>'
        return mark_safe(html)
    items_list.short_description = 'Список заказанного оборудования'
    
    def contact_info(self, obj):
        """Отображение контактной информации"""
        info = f'<strong>Имя:</strong> {escape(obj.customer_name)}<br>'
        info += f'<strong>Телефон:</strong> {escape(obj.customer_phone)}<br>'
        if obj.customer_email:
            info += f'<strong>Email:</strong> {escape(obj.customer_email)}<br>'
        if obj.customer_comment:
            info += f'<strong>Комментарий:</strong> {escape(obj.customer_comment)}<br>'
        # Добавляем информацию о дате и времени монтажа
        if obj.installation_date:
            date_str = obj.installation_date.strftime('%d.%m.%Y')
            time_str = obj.installation_time.strftime('%H:%M') if obj.installation_time else ''
            if time_str:
                info += f'<strong>Дата/время монтажа:</strong> {date_str} {time_str}'
            else:
                info += f'<strong>Дата монтажа:</strong> {date_str}'
        return mark_safe(info)
    contact_info.short_description = 'Контактные данные'
    
    def save_model(self, request, obj, form, change):
        """Пересчитываем общую сумму при сохранении"""
        super().save_model(request, obj, form, change)
        # Пересчитываем общую сумму из позиций
        obj.total_amount = obj.get_total_price()
        obj.save(update_fields=['total_amount'])
    
    actions = [
        'mark_as_processing', 
        'mark_as_completed', 
        'mark_as_cancelled',
        'delete_obsolete_orders',
        'delete_old_completed_orders',
        'delete_old_cancelled_orders',
        'delete_all_obsolete_orders',
    ]
    
    def mark_as_processing(self, request, queryset):
        count = queryset.update(status='processing')
        messages.success(request, f'{count} заказ(ов) отмечено как "В обработке"')
    mark_as_processing.short_description = 'Отметить как "В обработке"'
    
    def mark_as_completed(self, request, queryset):
        count = queryset.update(status='completed')
        messages.success(request, f'{count} заказ(ов) отмечено как "Завершен"')
    mark_as_completed.short_description = 'Отметить как "Завершен"'
    
    def mark_as_cancelled(self, request, queryset):
        count = queryset.update(status='cancelled')
        messages.success(request, f'{count} заказ(ов) отмечено как "Отменен"')
    mark_as_cancelled.short_description = 'Отметить как "Отменен"'
    
    def delete_obsolete_orders(self, request, queryset):
        """Удаление неактуальных заказов (завершенных и отмененных)"""
        obsolete_orders = queryset.filter(status__in=['completed', 'cancelled'])
        count = obsolete_orders.count()
        
        if count == 0:
            messages.warning(request, 'Нет неактуальных заказов для удаления')
            return
        
        # Удаляем заказы (связанные OrderItem удалятся автоматически из-за CASCADE)
        obsolete_orders.delete()
        messages.success(request, f'Удалено {count} неактуальных заказ(ов)')
    delete_obsolete_orders.short_description = '🗑️ Удалить выбранные неактуальные заказы (завершенные/отмененные)'
    
    def delete_old_completed_orders(self, request, queryset):
        """Удаление старых завершенных заказов (старше 6 месяцев)"""
        six_months_ago = timezone.now() - timedelta(days=180)
        old_completed = queryset.filter(
            status='completed',
            created_at__lt=six_months_ago
        )
        count = old_completed.count()
        
        if count == 0:
            messages.warning(request, 'Нет старых завершенных заказов для удаления')
            return
        
        old_completed.delete()
        messages.success(request, f'Удалено {count} старых завершенных заказ(ов) (старше 6 месяцев)')
    delete_old_completed_orders.short_description = '🗑️ Удалить старые завершенные заказы (старше 6 месяцев)'
    
    def delete_old_cancelled_orders(self, request, queryset):
        """Удаление старых отмененных заказов (старше 3 месяцев)"""
        three_months_ago = timezone.now() - timedelta(days=90)
        old_cancelled = queryset.filter(
            status='cancelled',
            created_at__lt=three_months_ago
        )
        count = old_cancelled.count()
        
        if count == 0:
            messages.warning(request, 'Нет старых отмененных заказов для удаления')
            return
        
        old_cancelled.delete()
        messages.success(request, f'Удалено {count} старых отмененных заказ(ов) (старше 3 месяцев)')
    delete_old_cancelled_orders.short_description = '🗑️ Удалить старые отмененные заказы (старше 3 месяцев)'
    
    def delete_all_obsolete_orders(self, request, queryset):
        """Удаление всех неактуальных заказов из базы данных (независимо от выбора)"""
        # Удаляем старые завершенные заказы (старше 6 месяцев)
        six_months_ago = timezone.now() - timedelta(days=180)
        old_completed = Order.objects.filter(
            status='completed',
            created_at__lt=six_months_ago
        )
        completed_count = old_completed.count()
        old_completed.delete()
        
        # Удаляем старые отмененные заказы (старше 3 месяцев)
        three_months_ago = timezone.now() - timedelta(days=90)
        old_cancelled = Order.objects.filter(
            status='cancelled',
            created_at__lt=three_months_ago
        )
        cancelled_count = old_cancelled.count()
        old_cancelled.delete()
        
        total_count = completed_count + cancelled_count
        
        if total_count == 0:
            messages.info(request, 'Нет неактуальных заказов для удаления')
        else:
            messages.success(
                request, 
                f'Удалено {total_count} неактуальных заказ(ов): '
                f'{completed_count} завершенных (старше 6 мес.) и '
                f'{cancelled_count} отмененных (старше 3 мес.)'
            )
    delete_all_obsolete_orders.short_description = '🗑️ Удалить ВСЕ неактуальные заказы из базы (старые завершенные и отмененные)'


class UserProfileInline(admin.StackedInline):
    """Инлайн для отображения профиля пользователя в админке User"""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Профиль'
    fields = ('name_or_organization', 'phone', 'messenger_link', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')


class CustomUserAdmin(BaseUserAdmin):
    """Расширенная админ-панель для управления пользователями"""
    inlines = (UserProfileInline,)


# Регистрируем CustomUserAdmin вместо стандартного UserAdmin
# Отменяем регистрацию только если User уже зарегистрирован
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass
admin.site.register(User, CustomUserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Админ-панель для управления профилями пользователей"""
    list_display = ('user', 'name_or_organization', 'phone', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__email', 'name_or_organization', 'phone')
    readonly_fields = ('created_at', 'updated_at')
    fields = ('user', 'name_or_organization', 'phone', 'messenger_link', 'created_at', 'updated_at')
