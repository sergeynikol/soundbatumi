"""
Состояния для создания заказа
"""
from aiogram.fsm.state import State, StatesGroup


class OrderStates(StatesGroup):
    """Состояния процесса создания заказа"""
    waiting_for_name = State()  # Ожидание имени клиента
    waiting_for_phone = State()  # Ожидание телефона
    waiting_for_email = State()  # Ожидание email (опционально)
    waiting_for_address = State()  # Ожидание адреса доставки
    waiting_for_comment = State()  # Ожидание комментария (опционально)
    waiting_for_equipment_name = State()  # Ожидание названия оборудования
    waiting_for_equipment_quantity = State()  # Ожидание количества
    waiting_for_equipment_price = State()  # Ожидание цены за единицу
    waiting_for_more_items = State()  # Ожидание подтверждения добавления еще позиций
    confirm_order = State()  # Подтверждение заказа
