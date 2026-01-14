"""
Сервисы для работы с заказами в Django ORM
"""
import django
import os
import sys
from pathlib import Path

# Настройка Django
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
if BASE_DIR not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'soundbatumi.settings.dev')

try:
    django.setup()
except Exception as e:
    # Если Django уже настроен, игнорируем ошибку
    pass

from django.db import transaction
from django.utils import timezone
from home.models import Order, OrderItem
from home.bot.utils import generate_order_number


def create_order_from_bot(order_data: dict) -> tuple[bool, Order | None, str]:
    """
    Создает заказ в базе данных из данных бота
    
    Args:
        order_data: Словарь с данными заказа
        
    Returns:
        tuple: (success, order, message)
    """
    try:
        with transaction.atomic():
            # Генерируем номер заказа
            order_number = generate_order_number()
            
            # Проверяем уникальность (маловероятно, но на всякий случай)
            while Order.objects.filter(order_number=order_number).exists():
                order_number = generate_order_number()
            
            # Создаем заказ
            order = Order.objects.create(
                order_number=order_number,
                delivery_address=order_data.get('delivery_address', ''),
                customer_name=order_data.get('customer_name', ''),
                customer_phone=order_data.get('customer_phone', ''),
                customer_email=order_data.get('customer_email') or None,
                customer_comment=order_data.get('customer_comment') or None,
                status='pending',
                user=None,  # Заказ из Telegram не привязан к пользователю
            )
            
            # Создаем позиции заказа
            total_amount = 0
            for item in order_data.get('items', []):
                total_price = item['unit_price'] * item['quantity']
                OrderItem.objects.create(
                    order=order,
                    equipment_name=item['equipment_name'],
                    equipment_id=item.get('equipment_id', ''),
                    quantity=item['quantity'],
                    unit_price=item['unit_price'],
                    total_price=total_price,
                    equipment_image=item.get('equipment_image', '') or None,
                )
                total_amount += float(total_price)
            
            # Обновляем общую сумму заказа
            order.total_amount = total_amount
            order.save()
            
            return True, order, f"Заказ #{order.order_number} успешно создан!"
            
    except Exception as e:
        return False, None, f"Ошибка при создании заказа: {str(e)}"
