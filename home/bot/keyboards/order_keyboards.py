"""
Клавиатуры для работы с заказами
"""
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Главное меню бота с основными командами"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="📦 Создать заказ"))
    builder.add(KeyboardButton(text="ℹ️ Помощь"))
    builder.add(KeyboardButton(text="❌ Отменить"))
    builder.adjust(2, 1)  # Первые две кнопки в ряд, последняя отдельно
    return builder.as_markup(resize_keyboard=True, persistent=True)


def get_skip_keyboard():
    """Клавиатура для пропуска опциональных полей"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="⏭️ Пропустить"))
    builder.add(KeyboardButton(text="❌ Отменить заказ"))
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


def get_yes_no_keyboard():
    """Клавиатура для подтверждения"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="✅ Да"))
    builder.add(KeyboardButton(text="❌ Нет"))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


def get_phone_keyboard():
    """Клавиатура для запроса телефона"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(
        text="📱 Отправить номер телефона",
        request_contact=True
    ))
    builder.add(KeyboardButton(text="❌ Отменить заказ"))
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


def get_more_items_keyboard():
    """Клавиатура для добавления еще позиций"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="➕ Добавить еще позицию"))
    builder.add(KeyboardButton(text="✅ Завершить заказ"))
    builder.add(KeyboardButton(text="❌ Отменить заказ"))
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


def get_confirm_order_keyboard():
    """Клавиатура для подтверждения заказа"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="✅ Подтвердить заказ"))
    builder.add(KeyboardButton(text="✏️ Изменить данные"))
    builder.add(KeyboardButton(text="❌ Отменить заказ"))
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


def get_cancel_keyboard():
    """Клавиатура для отмены"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="❌ Отменить заказ"))
    return builder.as_markup(resize_keyboard=True)
