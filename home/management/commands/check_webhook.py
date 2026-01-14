"""
Django management command для проверки и настройки Telegram webhook
"""
import os
import requests
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Проверяет и настраивает Telegram webhook'

    def add_arguments(self, parser):
        parser.add_argument(
            '--set',
            type=str,
            help='URL для установки webhook (например, https://yourdomain.com/api/telegram-callback/)',
        )
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Удалить webhook',
        )

    def handle(self, *args, **options):
        bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        
        if not bot_token:
            self.stdout.write(
                self.style.ERROR('❌ TELEGRAM_BOT_TOKEN не настроен в settings')
            )
            return
        
        # Проверяем текущий webhook
        check_url = f'https://api.telegram.org/bot{bot_token}/getWebhookInfo'
        response = requests.get(check_url, timeout=10)
        
        if response.status_code == 200:
            webhook_info = response.json()
            if webhook_info.get('ok'):
                info = webhook_info.get('result', {})
                self.stdout.write('\n📋 Текущая информация о webhook:')
                self.stdout.write(f'   URL: {info.get("url", "не установлен")}')
                self.stdout.write(f'   Ожидает подтверждения: {info.get("pending_update_count", 0)} обновлений')
                self.stdout.write(f'   Последняя ошибка: {info.get("last_error_message", "нет")}')
                self.stdout.write(f'   Последняя ошибка (дата): {info.get("last_error_date", "нет")}')
                
                if options['delete']:
                    # Удаляем webhook
                    delete_url = f'https://api.telegram.org/bot{bot_token}/deleteWebhook'
                    delete_response = requests.post(delete_url, timeout=10)
                    if delete_response.status_code == 200:
                        result = delete_response.json()
                        if result.get('ok'):
                            self.stdout.write(
                                self.style.SUCCESS('\n✅ Webhook успешно удален')
                            )
                        else:
                            self.stdout.write(
                                self.style.ERROR(f'\n❌ Ошибка при удалении webhook: {result.get("description")}')
                            )
                    else:
                        self.stdout.write(
                            self.style.ERROR(f'\n❌ HTTP ошибка при удалении webhook: {delete_response.status_code}')
                        )
                    return
                
                if options['set']:
                    # Устанавливаем webhook
                    webhook_url = options['set']
                    set_url = f'https://api.telegram.org/bot{bot_token}/setWebhook'
                    set_response = requests.post(
                        set_url,
                        json={'url': webhook_url},
                        timeout=10
                    )
                    
                    if set_response.status_code == 200:
                        result = set_response.json()
                        if result.get('ok'):
                            self.stdout.write(
                                self.style.SUCCESS(f'\n✅ Webhook успешно установлен: {webhook_url}')
                            )
                            # Проверяем еще раз
                            check_response = requests.get(check_url, timeout=10)
                            if check_response.status_code == 200:
                                check_result = check_response.json()
                                if check_result.get('ok'):
                                    new_info = check_result.get('result', {})
                                    self.stdout.write(f'   Подтвержден: {new_info.get("url") == webhook_url}')
                        else:
                            self.stdout.write(
                                self.style.ERROR(f'\n❌ Ошибка при установке webhook: {result.get("description")}')
                            )
                    else:
                        self.stdout.write(
                            self.style.ERROR(f'\n❌ HTTP ошибка при установке webhook: {set_response.status_code}')
                        )
                    return
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ Ошибка при получении информации о webhook: {webhook_info.get("description")}')
                )
        else:
            self.stdout.write(
                self.style.ERROR(f'❌ HTTP ошибка при проверке webhook: {response.status_code}')
            )
        
        # Если не указаны опции, просто показываем информацию
        if not options['set'] and not options['delete']:
            self.stdout.write('\n💡 Использование:')
            self.stdout.write('   python manage.py check_webhook --set https://yourdomain.com/api/telegram-callback/')
            self.stdout.write('   python manage.py check_webhook --delete')
