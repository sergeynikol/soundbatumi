"""
Wagtail админ-панель для управления заказами
"""
from wagtail.admin.viewsets.model import ModelViewSet
from wagtail.admin.ui.tables import UpdatedAtColumn
from wagtail import hooks
from django.utils.html import format_html, escape
from django.utils.safestring import mark_safe
from django.utils import timezone
from django.contrib import messages
from datetime import timedelta
from .models import Order


class OrderViewSet(ModelViewSet):
    """ViewSet для управления заказами в Wagtail админ-панели"""
    model = Order
    menu_label = "Заказы"
    menu_icon = "list-ul"
    menu_order = 200
    inspect_view_enabled = True
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
        """Оптимизация запросов - предзагрузка связанных объектов"""
        queryset = super().get_queryset(request)
        return queryset.prefetch_related('items')


order_viewset = OrderViewSet("order")
