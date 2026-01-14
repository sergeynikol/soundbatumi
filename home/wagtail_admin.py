"""
Wagtail админ-панель для управления заказами и пользователями.

Этот модуль содержит ViewSet'ы для настройки интерфейса админ-панели Wagtail
для работы с заказами и пользователями.
"""
from wagtail.admin.viewsets.model import ModelViewSet
from wagtail.admin.ui.tables import UpdatedAtColumn
from django.utils.html import format_html, escape
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User
from .models import Order, UserProfile


class OrderViewSet(ModelViewSet):
    """
    ViewSet для управления заказами в Wagtail админ-панели.
    
    Настраивает отображение, фильтрацию, поиск и редактирование заказов
    в интерфейсе администратора Wagtail.
    """
    model = Order
    menu_label = "Заказы"
    menu_icon = "list-ul"
    menu_order = 200
    inspect_view_enabled = True
    list_per_page = 50
    # Используем кастомный шаблон для добавления bulk actions
    index_template_name = 'wagtailadmin/order/index.html'
    inspect_view_fields = [
        'order_number',
        'created_at',
        'status',
        'user',
        'customer_name',
        'customer_phone',
        'customer_email',
        'delivery_address',
        'customer_comment',
        'total_amount',
    ]
    
    form_fields = [
        'status',
        'user',
        'customer_name',
        'customer_phone',
        'customer_email',
        'delivery_address',
        'customer_comment',
    ]
    
    exclude_form_fields = ['order_number', 'created_at', 'total_amount']
    
    list_display = [
        'order_number',
        'customer_name',
        'customer_phone',
        'get_equipment_list_short',
        'user',
        'status',
        'total_amount',
        UpdatedAtColumn(),
    ]
    
    list_filter = ['status', 'created_at']
    search_fields = ['order_number', 'customer_name', 'customer_phone', 'customer_email']
    ordering = ['-created_at']
    
    def get_queryset(self, request):
        """
        Оптимизация запросов - предзагрузка связанных объектов.
        
        Использует prefetch_related для уменьшения количества запросов к БД
        при отображении списка заказов с их позициями.
        
        Args:
            request: HTTP запрос
            
        Returns:
            QuerySet: Оптимизированный queryset с предзагруженными позициями заказов
        """
        queryset = super().get_queryset(request)
        return queryset.prefetch_related('items')


order_viewset = OrderViewSet("order")


class UserViewSet(ModelViewSet):
    """
    ViewSet для управления пользователями в Wagtail админ-панели.
    
    Настраивает отображение, фильтрацию, поиск и редактирование пользователей
    в интерфейсе администратора Wagtail. Включает отображение профилей пользователей.
    """
    model = User
    menu_label = "Пользователи"
    menu_icon = "user"
    menu_order = 100
    inspect_view_enabled = True
    inspect_view_fields = [
        'username',
        'email',
        'first_name',
        'last_name',
        'is_staff',
        'is_superuser',
        'is_active',
        'date_joined',
        'last_login',
        'get_user_profile',
    ]
    
    form_fields = [
        'username',
        'email',
        'first_name',
        'last_name',
        'is_staff',
        'is_superuser',
        'is_active',
    ]
    
    exclude_form_fields = ['password', 'date_joined', 'last_login']
    
    list_display = [
        'username',
        'email',
        'first_name',
        'last_name',
        'is_staff',
        'is_superuser',
        'is_active',
        'date_joined',
        UpdatedAtColumn(),
    ]
    
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    def get_user_profile(self, obj):
        """
        Отображение полной информации о профиле в детальном просмотре.
        
        Форматирует информацию о профиле пользователя в HTML для отображения
        в детальном просмотре заказа в админ-панели.
        
        Args:
            obj: Объект пользователя (User)
            
        Returns:
            str: HTML строка с информацией о профиле
        """
        try:
            profile = obj.profile
            html = '<div style="padding: 15px; background: #f8f9fa; border-radius: 5px;">'
            html += '<h4 style="margin-top: 0;">Информация о профиле</h4>'
            
            if profile.name_or_organization:
                html += f'<p><strong>Имя/Организация:</strong> {escape(profile.name_or_organization)}</p>'
            if profile.phone:
                html += f'<p><strong>Телефон:</strong> {escape(profile.phone)}</p>'
            if profile.messenger_link:
                html += f'<p><strong>Мессенджер:</strong> <a href="{escape(profile.messenger_link)}" target="_blank">{escape(profile.messenger_link)}</a></p>'
            if profile.created_at:
                html += f'<p><strong>Профиль создан:</strong> {profile.created_at.strftime("%d.%m.%Y %H:%M")}</p>'
            if profile.updated_at:
                html += f'<p><strong>Профиль обновлен:</strong> {profile.updated_at.strftime("%d.%m.%Y %H:%M")}</p>'
            
            html += '</div>'
            return mark_safe(html)
        except UserProfile.DoesNotExist:
            return format_html('<p style="color: #999;">Профиль пользователя не создан</p>')
    get_user_profile.short_description = 'Профиль пользователя'


user_viewset = UserViewSet("user")
