"""
Утилиты для отправки уведомлений в Telegram
"""
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def send_order_notification(order):
    """
    Отправляет уведомление о новом заказе в Telegram группу
    
    Args:
        order: Объект Order
    """
    bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    group_id = getattr(settings, 'TELEGRAM_GROUP_ID', None)
    
    if not bot_token:
        logger.warning(
            f'TELEGRAM_BOT_TOKEN не настроен, уведомление не отправлено. '
            f'Заказ: {order.order_number}'
        )
        return False
    
    # Проверяем наличие ID группы (учитываем пустые строки)
    if not group_id or (isinstance(group_id, str) and not group_id.strip()):
        # Если группа не настроена, пробуем использовать старый способ (личные чаты)
        admin_ids_str = getattr(settings, 'TELEGRAM_ADMIN_IDS', '')
        if not admin_ids_str:
            logger.warning(
                f'TELEGRAM_GROUP_ID и TELEGRAM_ADMIN_IDS не настроены, уведомление не отправлено. '
                f'Заказ: {order.order_number}'
            )
            return False
        
        # Парсим ID администраторов для обратной совместимости
        try:
            admin_ids = [
                int(admin_id.strip())
                for admin_id in admin_ids_str.split(',')
                if admin_id.strip()
            ]
        except ValueError:
            logger.error(
                f'Ошибка парсинга TELEGRAM_ADMIN_IDS: {admin_ids_str}. '
                f'Заказ: {order.order_number}'
            )
            return False
        
        if not admin_ids:
            logger.warning(
                f'Не найдено валидных ID администраторов. '
                f'Заказ: {order.order_number}'
            )
            return False
        
        # Отправляем в личные чаты (старый способ)
        return _send_to_private_chats(order, bot_token, admin_ids)
    
    # Парсим ID группы (может быть строкой или числом)
    try:
        if isinstance(group_id, str):
            # Если это строка, убираем @ если есть и парсим как число
            group_id = group_id.replace('@', '').strip()
            # Если это числовая строка, конвертируем в int
            # Если это username группы, оставляем как строку
            try:
                group_id = int(group_id)
            except ValueError:
                # Это username группы (например, @mygroup)
                group_id = f'@{group_id}' if not group_id.startswith('@') else group_id
        elif isinstance(group_id, int):
            # Если это число, используем как есть, но делаем отрицательным для групп
            # (Telegram использует отрицательные ID для групп)
            if group_id > 0:
                group_id = -group_id
    except Exception as e:
        logger.error(
            f'Ошибка обработки TELEGRAM_GROUP_ID: {group_id}. '
            f'Заказ: {order.order_number}, ошибка: {e}'
        )
        return False
    
    # Отправляем сообщение в группу
    return _send_to_group(order, bot_token, group_id)


def _send_to_group(order, bot_token, group_id):
    """
    Отправляет уведомление о заказе в группу Telegram
    
    Args:
        order: Объект Order
        bot_token: Токен бота
        group_id: ID группы (может быть числом или username)
    """
    # Формируем сообщение
    try:
        message = format_order_message(order)
        if not message or len(message.strip()) == 0:
            logger.error(
                f'Не удалось сформировать сообщение для заказа {order.order_number}'
            )
            return False
    except Exception as e:
        logger.error(
            f'Ошибка при формировании сообщения для заказа {order.order_number}: {e}',
            exc_info=True
        )
        return False
    
    # Отправляем сообщение в группу
    try:
        url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
        
        # Создаем inline кнопку "В обработку"
        inline_keyboard = {
            'inline_keyboard': [[
                {
                    'text': '✅ В обработку',
                    'callback_data': f'process_order_{order.id}'
                }
            ]]
        }
        
        payload = {
            'chat_id': group_id,
            'text': message,
            'parse_mode': 'HTML',
            'reply_markup': inline_keyboard
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        # Проверяем ответ API
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                logger.info(
                    f'Уведомление успешно отправлено в группу {group_id} '
                    f'для заказа {order.order_number}'
                )
                return True
            else:
                error_description = result.get('description', 'Unknown error')
                logger.error(
                    f'Ошибка API Telegram при отправке в группу {group_id}: '
                    f'{error_description}. Заказ: {order.order_number}'
                )
                return False
        else:
            try:
                error_data = response.json()
                error_description = error_data.get('description', f'HTTP {response.status_code}')
            except:
                error_description = f'HTTP {response.status_code}: {response.text}'
            
            logger.error(
                f'HTTP ошибка при отправке в группу {group_id}: '
                f'{error_description}. Заказ: {order.order_number}'
            )
            return False
    except requests.RequestException as e:
        logger.error(
            f'Ошибка отправки уведомления в группу {group_id}: {e}. '
            f'Заказ: {order.order_number}',
            exc_info=True
        )
        return False
    except Exception as e:
        logger.error(
            f'Неожиданная ошибка при отправке уведомления '
            f'в группу {group_id}: {e}. Заказ: {order.order_number}',
            exc_info=True
        )
        return False


def _send_to_private_chats(order, bot_token, admin_ids):
    """
    Отправляет уведомление о заказе в личные чаты администраторов (старый способ)
    
    Args:
        order: Объект Order
        bot_token: Токен бота
        admin_ids: Список ID администраторов
    """
    # Формируем сообщение
    try:
        message = format_order_message(order)
        if not message or len(message.strip()) == 0:
            logger.error(
                f'Не удалось сформировать сообщение для заказа {order.order_number}'
            )
            return False
    except Exception as e:
        logger.error(
            f'Ошибка при формировании сообщения для заказа {order.order_number}: {e}',
            exc_info=True
        )
        return False
    
    # Отправляем сообщение каждому администратору
    success_count = 0
    for admin_id in admin_ids:
        try:
            url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
            
            # Создаем inline кнопку "В обработку"
            # В callback_data передаем order_number и message_id для идентификации
            inline_keyboard = {
                'inline_keyboard': [[
                    {
                        'text': '✅ В обработку',
                        'callback_data': f'process_order_{order.id}'
                    }
                ]]
            }
            
            payload = {
                'chat_id': admin_id,
                'text': message,
                'parse_mode': 'HTML',
                'reply_markup': inline_keyboard
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            # Проверяем ответ API
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    success_count += 1
                    logger.info(
                        f'Уведомление успешно отправлено администратору {admin_id} '
                        f'для заказа {order.order_number}'
                    )
                else:
                    error_description = result.get('description', 'Unknown error')
                    # Специальная обработка для ошибки "bots can't send messages to bots"
                    if 'bots can\'t send messages to bots' in error_description or 'bot' in error_description.lower():
                        logger.error(
                            f'❌ ОШИБКА: ID {admin_id} является ID бота, а не пользователя! '
                            f'Боты не могут отправлять сообщения другим ботам. '
                            f'Проверьте TELEGRAM_ADMIN_IDS в настройках. Заказ: {order.order_number}'
                        )
                    else:
                        logger.error(
                            f'Ошибка API Telegram при отправке администратору {admin_id}: '
                            f'{error_description}. Заказ: {order.order_number}'
                        )
            else:
                try:
                    error_data = response.json()
                    error_description = error_data.get('description', f'HTTP {response.status_code}')
                except:
                    error_description = f'HTTP {response.status_code}: {response.text}'
                
                # Специальная обработка для ошибки "bots can't send messages to bots"
                if 'bots can\'t send messages to bots' in error_description or 'bot' in error_description.lower():
                    logger.error(
                        f'❌ ОШИБКА: ID {admin_id} является ID бота, а не пользователя! '
                        f'Боты не могут отправлять сообщения другим ботам. '
                        f'Проверьте TELEGRAM_ADMIN_IDS в настройках. Заказ: {order.order_number}'
                    )
                else:
                    logger.error(
                        f'HTTP ошибка при отправке администратору {admin_id}: '
                        f'{error_description}. Заказ: {order.order_number}'
                    )
        except requests.RequestException as e:
            logger.error(
                f'Ошибка отправки уведомления администратору {admin_id}: {e}. '
                f'Заказ: {order.order_number}',
                exc_info=True
            )
        except Exception as e:
            logger.error(
                f'Неожиданная ошибка при отправке уведомления '
                f'администратору {admin_id}: {e}. Заказ: {order.order_number}',
                exc_info=True
            )
    
    if success_count > 0:
        logger.info(
            f'Уведомление о заказе {order.order_number} отправлено '
            f'{success_count} из {len(admin_ids)} администраторов'
        )
        return True
    else:
        logger.error(
            f'Не удалось отправить уведомление о заказе '
            f'{order.order_number} ни одному администратору'
        )
        return False


def format_order_message(order):
    """
    Форматирует сообщение о заказе для Telegram
    
    Args:
        order: Объект Order
        
    Returns:
        str: Отформатированное сообщение
    """
    # Получаем позиции заказа
    items = order.items.all()
    
    # Формируем список позиций
    items_text = []
    for i, item in enumerate(items, 1):
        items_text.append(
            f"{i}. <b>{item.equipment_name}</b>\n"
            f"   Количество: {item.quantity}\n"
            f"   Цена за единицу: {item.unit_price:.2f} ₾\n"
            f"   Итого: {item.total_price:.2f} ₾"
        )
    
    # Формируем сообщение
    # Первой строкой идет дата и время монтажа (выделено)
    message = ""
    
    if order.installation_date:
        date_str = order.installation_date.strftime('%d.%m.%Y')
        time_str = order.installation_time.strftime('%H:%M') if order.installation_time else ''
        if time_str:
            installation_info = f"🔧 <b><i>📅 МОНТАЖ: {date_str} в {time_str}</i></b>"
        else:
            installation_info = f"🔧 <b><i>📅 МОНТАЖ: {date_str}</i></b>"
        # Используем специальные символы для визуального выделения
        message = f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        message += f"{installation_info}\n"
        message += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    else:
        message = f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        message += f"🔧 <b><i>📅 МОНТАЖ: Дата не указана</i></b>\n"
        message += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    message += (
        f"🆕 <b>Новый заказ #{order.order_number}</b>\n\n"
        f"👤 <b>Клиент:</b> {order.customer_name}\n"
        f"📱 <b>Телефон:</b> {order.customer_phone}\n"
    )
    
    if order.customer_email:
        message += f"📧 <b>Email:</b> {order.customer_email}\n"
    
    message += f"📍 <b>Адрес доставки:</b> {order.delivery_address}\n"
    
    if order.customer_comment:
        message += f"💬 <b>Комментарий:</b> {order.customer_comment}\n"
    
    if order.user:
        message += (
            f"👤 <b>Пользователь:</b> {order.user.username} "
            f"(ID: {order.user.id})\n"
        )
    
    message += f"\n📋 <b>Позиции заказа:</b>\n\n"
    message += "\n\n".join(items_text)
    message += f"\n\n💰 <b>Общая сумма:</b> {order.total_amount:.2f} ₾"
    message += f"\n📅 <b>Дата создания:</b> {order.created_at.strftime('%d.%m.%Y %H:%M')}"
    
    return message
