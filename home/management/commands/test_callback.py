"""
Команда для тестирования callback обработки кнопки "В обработку"
"""
from django.core.management.base import BaseCommand
from django.conf import settings
import requests
import json
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Тестирует обработку callback запроса для кнопки "В обработку"'

    def add_arguments(self, parser):
        parser.add_argument(
            '--order-id',
            type=int,
            help='ID заказа для тестирования',
        )
        parser.add_argument(
            '--chat-id',
            type=str,
            help='ID чата (группы) где находится сообщение',
        )
        parser.add_argument(
            '--message-id',
            type=int,
            help='ID сообщения в группе',
        )
        parser.add_argument(
            '--user-id',
            type=int,
            help='ID пользователя, который нажимает кнопку',
        )

    def handle(self, *args, **options):
        order_id = options.get('order_id')
        chat_id = options.get('chat_id')
        message_id = options.get('message_id')
        user_id = options.get('user_id')
        
        if not all([order_id, chat_id, message_id, user_id]):
            self.stdout.write(
                self.style.ERROR(
                    'Необходимо указать все параметры: --order-id, --chat-id, --message-id, --user-id'
                )
            )
            self.stdout.write(
                'Пример: python manage.py test_callback --order-id 1 --chat-id -1001234567890 --message-id 123 --user-id 123456789'
            )
            return
        
        bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        if not bot_token:
            self.stdout.write(self.style.ERROR('TELEGRAM_BOT_TOKEN не настроен'))
            return
        
        # Формируем тестовый callback запрос
        callback_data = {
            'callback_query': {
                'id': 'test_callback_query_id',
                'from': {
                    'id': user_id,
                    'first_name': 'Test',
                    'username': 'testuser'
                },
                'message': {
                    'message_id': message_id,
                    'chat': {
                        'id': int(chat_id) if chat_id.lstrip('-').isdigit() else chat_id,
                        'type': 'group'
                    }
                },
                'data': f'process_order_{order_id}'
            }
        }
        
        self.stdout.write(self.style.SUCCESS('Отправка тестового callback запроса...'))
        self.stdout.write(f'Данные: {json.dumps(callback_data, indent=2, ensure_ascii=False)}')
        
        # Получаем URL для webhook
        webhook_url = getattr(settings, 'TELEGRAM_WEBHOOK_URL', None)
        if not webhook_url:
            # Пробуем определить URL из настроек
            base_url = getattr(settings, 'WAGTAILADMIN_BASE_URL', 'http://127.0.0.1:8000')
            webhook_url = f'{base_url}/api/telegram-callback/'
            self.stdout.write(
                self.style.WARNING(
                    f'TELEGRAM_WEBHOOK_URL не настроен, используем: {webhook_url}'
                )
            )
        
        try:
            response = requests.post(
                webhook_url,
                json=callback_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            self.stdout.write(f'Статус ответа: {response.status_code}')
            self.stdout.write(f'Ответ: {response.text}')
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    self.stdout.write(self.style.SUCCESS('✅ Callback обработан успешно!'))
                else:
                    self.stdout.write(
                        self.style.ERROR(f'❌ Ошибка: {result.get("error", "Unknown")}')
                    )
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ HTTP ошибка: {response.status_code}')
                )
                
        except requests.exceptions.RequestException as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Ошибка при отправке запроса: {e}')
            )
            self.stdout.write(
                self.style.WARNING(
                    'Убедитесь, что сервер Django запущен и доступен по адресу webhook URL'
                )
            )
