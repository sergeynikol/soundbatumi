"""
Management команда для запуска Telegram бота
"""
import asyncio
import logging
import os
import sys
from django.core.management.base import BaseCommand
from django.conf import settings

logger = logging.getLogger(__name__)

# Импортируем bot только после настройки Django
def import_bot():
    """Импорт функций бота после настройки Django"""
    from home.bot.bot import start_bot
    return start_bot


class Command(BaseCommand):
    help = 'Запускает Telegram бота для приема заказов'

    def add_arguments(self, parser):
        parser.add_argument(
            '--token',
            type=str,
            help='Telegram Bot Token (переопределяет переменную окружения)',
        )

    def handle(self, *args, **options):
        token = options.get('token')
        if token:
            # Убираем пробелы из токена
            token = token.strip()
            os.environ['TELEGRAM_BOT_TOKEN'] = token
            self.stdout.write(self.style.SUCCESS(f'✅ Токен установлен из командной строки (первые 10 символов: {token[:10]}...)'))
        else:
            # Проверяем, установлен ли токен в settings или переменных окружения
            token_from_settings = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
            token_from_env = os.getenv('TELEGRAM_BOT_TOKEN', None)
            
            if not token_from_settings and not token_from_env:
                self.stdout.write(self.style.ERROR(
                    '\n❌ TELEGRAM_BOT_TOKEN не установлен!\n\n'
                    'Пожалуйста, установите токен бота одним из способов:\n'
                    '1. В файле .env: TELEGRAM_BOT_TOKEN=your_token_here\n'
                    '2. В Django settings: TELEGRAM_BOT_TOKEN = "your_token_here"\n'
                    '3. Через командную строку: python manage.py run_bot --token your_token_here\n\n'
                    'Для получения токена создайте бота через @BotFather в Telegram.\n'
                    'Токен должен быть в формате: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz'
                ))
                return
            else:
                self.stdout.write(self.style.SUCCESS('✅ Токен найден в настройках'))
        
        # Импортируем функцию запуска бота после настройки Django
        start_bot = import_bot()
        
        try:
            self.stdout.write(self.style.SUCCESS('\n🚀 Запуск Telegram бота...\n'))
            asyncio.run(start_bot())
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\n\n⏹️  Остановка бота...'))
        except ValueError as e:
            # Это ошибки валидации токена
            self.stdout.write(self.style.ERROR(f'\n{str(e)}\n'))
            logger.error(f'Ошибка валидации: {e}')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Ошибка: {e}\n'))
            logger.error(f'Ошибка при запуске бота: {e}', exc_info=True)
