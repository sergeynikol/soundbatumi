"""
Общие обработчики команд
"""
from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from home.bot.keyboards.order_keyboards import get_main_menu_keyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    await state.clear()
    await message.answer(
        "👋 <b>Добро пожаловать в бот Sound Batumi!</b>\n\n"
        "Я помогу вам создать заказ на оборудование.\n\n"
        "📋 <b>Доступные команды:</b>\n"
        "/order - Создать новый заказ\n"
        "/help - Показать справку\n"
        "/cancel - Отменить текущий заказ\n\n"
        "Или используйте кнопки меню ниже 👇",
        reply_markup=get_main_menu_keyboard(),
        parse_mode='HTML'
    )


@router.message(Command("help"))
async def cmd_help(message: Message, state: FSMContext):
    """Обработчик команды /help"""
    await message.answer(
        "ℹ️ <b>Справка по использованию бота</b>\n\n"
        "Для создания заказа вам необходимо предоставить:\n\n"
        "1️⃣ <b>Имя клиента</b> - ваше имя или название организации\n"
        "2️⃣ <b>Номер телефона</b> - контактный телефон\n"
        "3️⃣ <b>Email</b> - электронная почта (необязательно)\n"
        "4️⃣ <b>Адрес доставки</b> - куда доставить заказ\n"
        "5️⃣ <b>Комментарий</b> - дополнительная информация "
        "(необязательно)\n"
        "6️⃣ <b>Позиции заказа</b> - список оборудования с количеством "
        "и ценой\n\n"
        "Для начала создания заказа нажмите /order или используйте "
        "кнопку меню.",
        parse_mode='HTML'
    )


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    """Обработчик команды /cancel"""
    await state.clear()
    await message.answer(
        "❌ Заказ отменен.",
        reply_markup=get_main_menu_keyboard()
    )


@router.message(F.text == "ℹ️ Помощь")
async def help_button(message: Message, state: FSMContext):
    """Обработчик кнопки помощи"""
    await cmd_help(message, state)


@router.message(F.text == "❌ Отменить")
async def cancel_button(message: Message, state: FSMContext):
    """Обработчик кнопки отмены"""
    await cmd_cancel(message, state)
