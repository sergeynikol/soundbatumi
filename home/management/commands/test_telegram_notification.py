"""
Management команда для тестирования отправки уведомлений в Telegram
"""
from django.core.management.base import BaseCommand
from home.models import Order
from home.telegram_notifications import send_order_notification, format_order_message
from django.conf import settings
import requests


class Command(BaseCommand):
    help = 'Тестирует отправку уведомлений в Telegram'

    def add_arguments(self, parser):
        parser.add_argument(
            '--order-number',
            type=str,
            help='Номер заказа для тестирования (если не указан, используется последний заказ)',
        )
        parser.add_argument(
            '--test-message',
            action='store_true',
            help='Отправить простое тестовое сообщение без заказа',
        )

    def handle(self, *args, **options):
        bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        admin_ids_str = getattr(settings, 'TELEGRAM_ADMIN_IDS', '')

        if not bot_token:
            self.stdout.write(
                self.style.ERROR('❌ TELEGRAM_BOT_TOKEN не настроен!')
            )
            return

        if not admin_ids_str:
            self.stdout.write(
                self.style.ERROR('❌ TELEGRAM_ADMIN_IDS не настроен!')
            )
            return

        # Парсим ID администраторов
        try:
            admin_ids = [
                int(admin_id.strip())
                for admin_id in admin_ids_str.split(',')
                if admin_id.strip()
            ]
        except ValueError:
            self.stdout.write(
                self.style.ERROR(f'❌ Ошибка парсинга TELEGRAM_ADMIN_IDS: {admin_ids_str}')
            )
            return

        if not admin_ids:
            self.stdout.write(
                self.style.ERROR('❌ Не найдено валидных ID администраторов')
            )
            return

        # Проверяем информацию о боте
        self.stdout.write('=== Проверка бота ===')
        try:
            bot_info_url = f'https://api.telegram.org/bot{bot_token}/getMe'
            bot_info_response = requests.get(bot_info_url, timeout=10)
            bot_info = bot_info_response.json()
            
            if bot_info.get('ok'):
                bot_data = bot_info.get('result', {})
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Бот активен: @{bot_data.get("username")} '
                        f'({bot_data.get("first_name")})'
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ Ошибка получения информации о боте: {bot_info}')
                )
                return
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Ошибка при проверке бота: {e}')
            )
            return

        # Отправка тестового сообщения
        if options['test_message']:
            self.stdout.write('\n=== Отправка тестового сообщения ===')
            for admin_id in admin_ids:
                try:
                    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
                    payload = {
                        'chat_id': admin_id,
                        'text': '🧪 Тестовое сообщение от бота SoundBatumi'
                    }
                    response = requests.post(url, json=payload, timeout=10)
                    result = response.json()
                    
                    if result.get('ok'):
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'✅ Тестовое сообщение отправлено администратору {admin_id}'
                            )
                        )
                    else:
                        error_desc = result.get('description', 'Unknown error')
                        self.stdout.write(
                            self.style.ERROR(
                                f'❌ Ошибка отправки администратору {admin_id}: {error_desc}'
                            )
                        )
                        if 'bot was blocked' in error_desc.lower():
                            self.stdout.write(
                                self.style.WARNING(
                                    '   → Пользователь заблокировал бота. '
                                    'Попросите его разблокировать бота или начать диалог с /start'
                                )
                            )
                        elif 'chat not found' in error_desc.lower():
                            self.stdout.write(
                                self.style.WARNING(
                                    '   → Пользователь не начал диалог с ботом. '
                                    'Попросите его отправить команду /start боту'
                                )
                            )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'❌ Ошибка при отправке тестового сообщения администратору {admin_id}: {e}'
                        )
                    )
            return

        # Отправка уведомления для заказа
        order = None
        if options['order_number']:
            try:
                order = Order.objects.get(order_number=options['order_number'])
            except Order.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f'❌ Заказ {options["order_number"]} не найден'
                    )
                )
                return
        else:
            order = Order.objects.order_by('-created_at').first()
            if not order:
                self.stdout.write(
                    self.style.ERROR('❌ Заказы не найдены в базе данных')
                )
                return

        self.stdout.write(f'\n=== Тест отправки для заказа {order.order_number} ===')
        self.stdout.write(f'ID заказа: {order.id}')
        self.stdout.write(f'Дата создания: {order.created_at}')
        self.stdout.write(f'Статус: {order.status}')
        self.stdout.write(f'Позиций: {order.items.count()}')
        self.stdout.write(f'Сумма: {order.total_amount} ₾')

        # Формируем сообщение
        try:
            message = format_order_message(order)
            self.stdout.write(f'\nДлина сообщения: {len(message)} символов')
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Ошибка при формировании сообщения: {e}')
            )
            return

        # Отправляем уведомление
        self.stdout.write('\n=== Отправка уведомления ===')
        result = send_order_notification(order)
        
        if result:
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Уведомление успешно отправлено для заказа {order.order_number}'
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    f'❌ Не удалось отправить уведомление для заказа {order.order_number}'
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    'Проверьте логи выше для получения подробной информации об ошибке'
                )
            )
