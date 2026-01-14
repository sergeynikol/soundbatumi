"""
Утилиты для бота
"""
import re
from decimal import Decimal, InvalidOperation
from datetime import datetime
import random


def validate_phone(phone: str) -> bool:
    """Валидация номера телефона"""
    # Убираем все нецифровые символы кроме +
    phone_clean = re.sub(r'[^\d+]', '', phone)
    # Проверяем, что длина от 10 до 15 символов
    return 10 <= len(phone_clean.replace('+', '')) <= 15


def validate_email(email: str) -> bool:
    """Валидация email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_price(price_str: str) -> tuple[bool, Decimal | None]:
    """Валидация цены"""
    try:
        # Убираем все символы кроме цифр, точки и запятой
        price_clean = re.sub(r'[^\d.,]', '', price_str.replace(',', '.'))
        if not price_clean:
            return False, None
        price = Decimal(price_clean)
        if price <= 0:
            return False, None
        return True, price
    except (InvalidOperation, ValueError):
        return False, None


def validate_quantity(quantity_str: str) -> tuple[bool, int | None]:
    """Валидация количества"""
    try:
        quantity = int(quantity_str.strip())
        if quantity <= 0:
            return False, None
        if quantity > 10000:  # Разумное ограничение
            return False, None
        return True, quantity
    except ValueError:
        return False, None


def generate_order_number() -> str:
    """Генерация номера заказа"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_suffix = random.randint(1000, 9999)
    return f"ORD-{timestamp}-{random_suffix}"


def format_order_summary(order_data: dict) -> str:
    """Форматирование сводки заказа для отображения"""
    items_text = []
    total = Decimal('0')
    
    for i, item in enumerate(order_data.get('items', []), 1):
        item_total = item['unit_price'] * item['quantity']
        total += item_total
        items_text.append(
            f"{i}. {item['equipment_name']}\n"
            f"   Количество: {item['quantity']}\n"
            f"   Цена за единицу: {item['unit_price']:.2f} ₾\n"
            f"   Итого: {item_total:.2f} ₾"
        )
    
    summary = (
        f"📦 <b>Сводка заказа</b>\n\n"
        f"👤 <b>Клиент:</b> {order_data.get('customer_name', 'Не указано')}\n"
        f"📱 <b>Телефон:</b> {order_data.get('customer_phone', 'Не указано')}\n"
    )
    
    if order_data.get('customer_email'):
        summary += f"📧 <b>Email:</b> {order_data.get('customer_email')}\n"
    
    summary += (
        f"📍 <b>Адрес доставки:</b> {order_data.get('delivery_address', 'Не указано')}\n"
    )
    
    if order_data.get('customer_comment'):
        summary += f"💬 <b>Комментарий:</b> {order_data.get('customer_comment')}\n"
    
    summary += f"\n📋 <b>Позиции заказа:</b>\n" + "\n\n".join(items_text)
    summary += f"\n\n💰 <b>Общая сумма:</b> {total:.2f} ₾"
    
    return summary
