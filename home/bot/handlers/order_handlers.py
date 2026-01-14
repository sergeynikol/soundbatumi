"""
Обработчики для создания заказов
"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from home.bot.states.order_states import OrderStates
from home.bot.keyboards.order_keyboards import (
    get_skip_keyboard, get_phone_keyboard, get_more_items_keyboard,
    get_confirm_order_keyboard, get_cancel_keyboard
)
from home.bot.utils import (
    validate_phone, validate_email, validate_price, validate_quantity,
    format_order_summary
)
from home.bot.services import create_order_from_bot

router = Router()


@router.message(Command("order"))
@router.message(F.text == "📦 Создать заказ")
async def cmd_order(message: Message, state: FSMContext):
    """Начало процесса создания заказа"""
    await state.clear()
    await state.set_state(OrderStates.waiting_for_name)
    await state.update_data(items=[])
    
    await message.answer(
        "📦 <b>Создание нового заказа</b>\n\n"
        "Пожалуйста, введите <b>имя клиента</b> или название организации:",
        reply_markup=get_cancel_keyboard(),
        parse_mode='HTML'
    )


@router.message(OrderStates.waiting_for_name, F.text)
async def process_name(message: Message, state: FSMContext):
    """Обработка имени клиента"""
    if message.text == "❌ Отменить заказ":
        await state.clear()
        await message.answer("❌ Заказ отменен.")
        return
    
    name = message.text.strip()
    if len(name) < 2:
        await message.answer("⚠️ Имя слишком короткое. Пожалуйста, введите корректное имя:")
        return
    
    if len(name) > 255:
        await message.answer("⚠️ Имя слишком длинное (максимум 255 символов). Пожалуйста, введите более короткое имя:")
        return
    
    await state.update_data(customer_name=name)
    await state.set_state(OrderStates.waiting_for_phone)
    
    await message.answer(
        f"✅ Имя сохранено: <b>{name}</b>\n\n"
        "Теперь укажите <b>номер телефона</b> для связи:",
        reply_markup=get_phone_keyboard(),
        parse_mode='HTML'
    )


@router.message(OrderStates.waiting_for_phone, F.contact)
async def process_phone_contact(message: Message, state: FSMContext):
    """Обработка номера телефона из контакта"""
    phone = message.contact.phone_number
    if not phone.startswith('+'):
        phone = '+' + phone
    
    await state.update_data(customer_phone=phone)
    await state.set_state(OrderStates.waiting_for_email)
    
    await message.answer(
        f"✅ Телефон сохранен: <b>{phone}</b>\n\n"
        "Введите <b>email</b> (или нажмите 'Пропустить', если не нужен):",
        reply_markup=get_skip_keyboard(),
        parse_mode='HTML'
    )


@router.message(OrderStates.waiting_for_phone, F.text)
async def process_phone_text(message: Message, state: FSMContext):
    """Обработка номера телефона в виде текста"""
    if message.text == "❌ Отменить заказ":
        await state.clear()
        await message.answer("❌ Заказ отменен.")
        return
    
    phone = message.text.strip()
    if not validate_phone(phone):
        await message.answer(
            "⚠️ Некорректный номер телефона. Пожалуйста, введите номер в формате:\n"
            "+995 XXX XXX XXX или используйте кнопку 'Отправить номер телефона'",
            reply_markup=get_phone_keyboard()
        )
        return
    
    await state.update_data(customer_phone=phone)
    await state.set_state(OrderStates.waiting_for_email)
    
    await message.answer(
        f"✅ Телефон сохранен: <b>{phone}</b>\n\n"
        "Введите <b>email</b> (или нажмите 'Пропустить', если не нужен):",
        reply_markup=get_skip_keyboard(),
        parse_mode='HTML'
    )


@router.message(OrderStates.waiting_for_email, F.text)
async def process_email(message: Message, state: FSMContext):
    """Обработка email"""
    if message.text == "⏭️ Пропустить":
        await state.update_data(customer_email=None)
        await state.set_state(OrderStates.waiting_for_address)
        await message.answer(
            "✅ Email пропущен.\n\n"
            "Теперь укажите <b>адрес доставки</b>:",
            reply_markup=get_cancel_keyboard(),
            parse_mode='HTML'
        )
        return
    
    if message.text == "❌ Отменить заказ":
        await state.clear()
        await message.answer("❌ Заказ отменен.")
        return
    
    email = message.text.strip()
    if not validate_email(email):
        await message.answer(
            "⚠️ Некорректный email адрес. Пожалуйста, введите корректный email или нажмите 'Пропустить':",
            reply_markup=get_skip_keyboard()
        )
        return
    
    await state.update_data(customer_email=email)
    await state.set_state(OrderStates.waiting_for_address)
    
    await message.answer(
        f"✅ Email сохранен: <b>{email}</b>\n\n"
        "Теперь укажите <b>адрес доставки</b>:",
        reply_markup=get_cancel_keyboard(),
        parse_mode='HTML'
    )


@router.message(OrderStates.waiting_for_address, F.text)
async def process_address(message: Message, state: FSMContext):
    """Обработка адреса доставки"""
    if message.text == "❌ Отменить заказ":
        await state.clear()
        await message.answer("❌ Заказ отменен.")
        return
    
    address = message.text.strip()
    if len(address) < 10:
        await message.answer("⚠️ Адрес слишком короткий. Пожалуйста, укажите полный адрес доставки:")
        return
    
    await state.update_data(delivery_address=address)
    await state.set_state(OrderStates.waiting_for_comment)
    
    await message.answer(
        f"✅ Адрес сохранен: <b>{address}</b>\n\n"
        "Введите <b>комментарий к заказу</b> (или нажмите 'Пропустить'):",
        reply_markup=get_skip_keyboard(),
        parse_mode='HTML'
    )


@router.message(OrderStates.waiting_for_comment, F.text)
async def process_comment(message: Message, state: FSMContext):
    """Обработка комментария"""
    if message.text == "⏭️ Пропустить":
        await state.update_data(customer_comment=None)
    elif message.text == "❌ Отменить заказ":
        await state.clear()
        await message.answer("❌ Заказ отменен.")
        return
    else:
        await state.update_data(customer_comment=message.text.strip())
    
    await state.set_state(OrderStates.waiting_for_equipment_name)
    await message.answer(
        "✅ Комментарий сохранен.\n\n"
        "Теперь добавим позиции заказа.\n"
        "Введите <b>название оборудования</b>:",
        reply_markup=get_cancel_keyboard(),
        parse_mode='HTML'
    )


@router.message(OrderStates.waiting_for_equipment_name, F.text)
async def process_equipment_name(message: Message, state: FSMContext):
    """Обработка названия оборудования"""
    if message.text == "❌ Отменить заказ":
        await state.clear()
        await message.answer("❌ Заказ отменен.")
        return
    
    equipment_name = message.text.strip()
    if len(equipment_name) < 3:
        await message.answer("⚠️ Название слишком короткое. Пожалуйста, введите полное название оборудования:")
        return
    
    await state.update_data(current_item={'equipment_name': equipment_name})
    await state.set_state(OrderStates.waiting_for_equipment_quantity)
    
    await message.answer(
        f"✅ Название сохранено: <b>{equipment_name}</b>\n\n"
        "Введите <b>количество</b> (целое число):",
        reply_markup=get_cancel_keyboard(),
        parse_mode='HTML'
    )


@router.message(OrderStates.waiting_for_equipment_quantity, F.text)
async def process_equipment_quantity(message: Message, state: FSMContext):
    """Обработка количества оборудования"""
    if message.text == "❌ Отменить заказ":
        await state.clear()
        await message.answer("❌ Заказ отменен.")
        return
    
    is_valid, quantity = validate_quantity(message.text)
    if not is_valid:
        await message.answer(
            "⚠️ Некорректное количество. Пожалуйста, введите целое положительное число (например: 5):",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    data = await state.get_data()
    current_item = data.get('current_item', {})
    current_item['quantity'] = quantity
    await state.update_data(current_item=current_item)
    await state.set_state(OrderStates.waiting_for_equipment_price)
    
    await message.answer(
        f"✅ Количество сохранено: <b>{quantity}</b>\n\n"
        "Введите <b>цену за единицу</b> в лари (например: 150.50):",
        reply_markup=get_cancel_keyboard(),
        parse_mode='HTML'
    )


@router.message(OrderStates.waiting_for_equipment_price, F.text)
async def process_equipment_price(message: Message, state: FSMContext):
    """Обработка цены оборудования"""
    if message.text == "❌ Отменить заказ":
        await state.clear()
        await message.answer("❌ Заказ отменен.")
        return
    
    is_valid, price = validate_price(message.text)
    if not is_valid:
        await message.answer(
            "⚠️ Некорректная цена. Пожалуйста, введите число (например: 150.50 или 150):",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    data = await state.get_data()
    current_item = data.get('current_item', {})
    current_item['unit_price'] = price
    current_item['equipment_id'] = ''  # Можно добавить позже
    current_item['equipment_image'] = ''  # Можно добавить позже
    current_item['total_price'] = price * current_item['quantity']
    
    # Добавляем позицию в список
    items = data.get('items', [])
    items.append(current_item)
    await state.update_data(items=items, current_item=None)
    
    total_items = len(items)
    total_amount = sum(item['unit_price'] * item['quantity'] for item in items)
    
    await message.answer(
        f"✅ Позиция добавлена!\n\n"
        f"📦 <b>Позиция {total_items}:</b>\n"
        f"Название: {current_item['equipment_name']}\n"
        f"Количество: {current_item['quantity']}\n"
        f"Цена: {price:.2f} ₾\n"
        f"Итого: {current_item['total_price']:.2f} ₾\n\n"
        f"<b>Всего позиций:</b> {total_items}\n"
        f"<b>Общая сумма:</b> {total_amount:.2f} ₾\n\n"
        "Добавить еще позицию или завершить заказ?",
        reply_markup=get_more_items_keyboard(),
        parse_mode='HTML'
    )
    
    await state.set_state(OrderStates.waiting_for_more_items)


@router.message(OrderStates.waiting_for_more_items, F.text)
async def process_more_items(message: Message, state: FSMContext):
    """Обработка добавления еще позиций"""
    if message.text == "➕ Добавить еще позицию":
        await state.set_state(OrderStates.waiting_for_equipment_name)
        await message.answer(
            "Введите <b>название следующего оборудования</b>:",
            reply_markup=get_cancel_keyboard(),
            parse_mode='HTML'
        )
    elif message.text == "✅ Завершить заказ":
        await show_order_summary(message, state)
    elif message.text == "❌ Отменить заказ":
        await state.clear()
        await message.answer("❌ Заказ отменен.")
    else:
        await message.answer(
            "Пожалуйста, выберите действие:",
            reply_markup=get_more_items_keyboard()
        )


async def show_order_summary(message: Message, state: FSMContext):
    """Показать сводку заказа для подтверждения"""
    data = await state.get_data()
    summary = format_order_summary(data)
    
    await message.answer(
        summary,
        reply_markup=get_confirm_order_keyboard(),
        parse_mode='HTML'
    )
    await state.set_state(OrderStates.confirm_order)


@router.message(OrderStates.confirm_order, F.text == "✅ Подтвердить заказ")
async def confirm_order(message: Message, state: FSMContext):
    """Подтверждение и создание заказа"""
    data = await state.get_data()
    
    # Проверяем обязательные поля
    required_fields = ['customer_name', 'customer_phone', 'delivery_address']
    missing_fields = [field for field in required_fields if not data.get(field)]
    
    if missing_fields:
        await message.answer(
            f"⚠️ Ошибка: отсутствуют обязательные поля: {', '.join(missing_fields)}"
        )
        return
    
    if not data.get('items'):
        await message.answer("⚠️ Ошибка: в заказе нет позиций.")
        return
    
    # Создаем заказ в базе данных
    success, order, message_text = create_order_from_bot(data)
    
    if success:
        await message.answer(
            f"✅ <b>Заказ успешно создан!</b>\n\n"
            f"{message_text}\n\n"
            f"📦 <b>Номер заказа:</b> {order.order_number}\n"
            f"📅 <b>Дата создания:</b> {order.created_at.strftime('%d.%m.%Y %H:%M')}\n"
            f"💰 <b>Сумма заказа:</b> {order.total_amount:.2f} ₾\n\n"
            "Спасибо за заказ! Мы свяжемся с вами в ближайшее время.",
            parse_mode='HTML'
        )
        await state.clear()
    else:
        await message.answer(
            f"❌ <b>Ошибка при создании заказа</b>\n\n{message_text}\n\n"
            "Пожалуйста, попробуйте еще раз или обратитесь в поддержку.",
            parse_mode='HTML'
        )


@router.message(OrderStates.confirm_order, F.text == "✏️ Изменить данные")
async def edit_order(message: Message, state: FSMContext):
    """Редактирование заказа - начинаем заново"""
    await message.answer(
        "Для изменения данных заказа, пожалуйста, начните создание заказа заново.\n"
        "Используйте /order или кнопку 'Создать заказ'.",
        reply_markup=get_cancel_keyboard()
    )


@router.message(OrderStates.confirm_order, F.text == "❌ Отменить заказ")
async def cancel_order_from_confirm(message: Message, state: FSMContext):
    """Отмена заказа из состояния подтверждения"""
    await state.clear()
    await message.answer("❌ Заказ отменен.")
