"""
Template tags для работы с ценами и скидками на оборудование
"""
from django import template
from decimal import Decimal, InvalidOperation
import re

register = template.Library()


def safe_decimal_conversion(value):
    """
    Безопасное преобразование значения в Decimal.
    Обрабатывает как числовые, так и текстовые значения.
    """
    if value is None:
        return None
    
    # Если это уже Decimal
    if isinstance(value, Decimal):
        return value
    
    # Если это число
    if isinstance(value, (int, float)):
        try:
            return Decimal(str(value))
        except (ValueError, InvalidOperation):
            return None
    
    # Если это строка, пытаемся извлечь число
    try:
        price_str = str(value).strip()
        if not price_str:
            return None
        
        # Удаляем все символы кроме цифр, точки и запятой
        price_clean = re.sub(r'[^\d.,]', '', price_str)
        if not price_clean:
            return None
        
        # Заменяем запятую на точку
        price_clean = price_clean.replace(',', '.')
        
        # Извлекаем первое число (может быть несколько чисел в строке)
        match = re.search(r'(\d+\.?\d*)', price_clean)
        if match:
            return Decimal(match.group(1))
        else:
            return None
    except (ValueError, TypeError, InvalidOperation, Exception):
        return None


@register.simple_tag
def get_equipment_price(equipment_block):
    """
    Вычисляет финальную цену с учетом индивидуальной и глобальной скидки
    
    Возвращает словарь:
    - original_price: исходная цена (число или строка)
    - final_price: цена со скидкой (число или строка)
    - has_discount: есть ли скидка
    - discount_source: источник скидки ('item', 'global')
    - global_discount: процент глобальной скидки
    - is_numeric: является ли цена числовой
    """
    # Получаем значение цены
    # StructValue ведет себя как словарь, поэтому используем доступ через словарь
    price_value = None
    if isinstance(equipment_block, dict):
        price_value = equipment_block.get('price_equipment')
    elif hasattr(equipment_block, '__getitem__'):
        # StructValue поддерживает доступ через []
        try:
            price_value = equipment_block['price_equipment']
        except (KeyError, TypeError):
            price_value = None
    elif hasattr(equipment_block, 'price_equipment'):
        price_value = equipment_block.price_equipment
    else:
        return {
            'original_price': '0',
            'final_price': '0',
            'has_discount': False,
            'discount_source': None,
            'global_discount': 0,
            'item_discount_percent': 0,
            'is_numeric': False,
        }
    
    # Пытаемся преобразовать в Decimal
    original_price_decimal = safe_decimal_conversion(price_value)
    
    # Если не удалось преобразовать в число, возвращаем как строку
    if original_price_decimal is None:
        return {
            'original_price': str(price_value),
            'final_price': str(price_value),
            'has_discount': False,
            'discount_source': None,
            'global_discount': 0,
            'item_discount_percent': 0,
            'is_numeric': False,
        }
    
    # Цена успешно преобразована в число
    original_price = original_price_decimal
    final_price = original_price
    has_discount = False
    discount_source = None
    global_discount = Decimal('0')
    
    # Получаем глобальные настройки скидки
    try:
        from home.models import EquipmentDiscountSettings
        global_settings = EquipmentDiscountSettings.get_settings()
        if global_settings.is_active:
            discount_val = safe_decimal_conversion(global_settings.discount_percent)
            if discount_val is not None:
                global_discount = discount_val
    except Exception:
        pass
    
    # Проверяем индивидуальную скидку товара
    item_discount = None
    discount_percent_value = None
    if isinstance(equipment_block, dict):
        discount_percent_value = equipment_block.get('discount_percent')
    elif hasattr(equipment_block, '__getitem__'):
        try:
            discount_percent_value = equipment_block['discount_percent']
        except (KeyError, TypeError):
            discount_percent_value = None
    elif hasattr(equipment_block, 'discount_percent'):
        discount_percent_value = equipment_block.discount_percent
    
    if discount_percent_value:
        item_discount = safe_decimal_conversion(discount_percent_value)
    
    # Применяем скидки (приоритет у индивидуальной скидки)
    if item_discount and item_discount > 0:
        # Индивидуальная скидка товара
        discount_amount = original_price * (item_discount / Decimal('100'))
        final_price = original_price - discount_amount
        has_discount = True
        discount_source = 'item'
    elif global_discount and global_discount > 0:
        # Глобальная скидка
        discount_amount = original_price * (global_discount / Decimal('100'))
        final_price = original_price - discount_amount
        has_discount = True
        discount_source = 'global'
    
    # Вычисляем процент скидки для отображения
    item_discount_percent = 0
    if item_discount and item_discount > 0:
        item_discount_percent = float(item_discount)
    
    return {
        'original_price': float(original_price),
        'final_price': float(final_price),
        'has_discount': has_discount,
        'discount_source': discount_source,
        'global_discount': float(global_discount),
        'item_discount_percent': item_discount_percent,
        'is_numeric': True,
    }
