"""
Главный файл бота
"""
import asyncio
import logging
import os
import sys
import django
from pathlib import Path

# Настройка Django перед импортом handlers
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
if BASE_DIR not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'soundbatumi.settings.dev')

try:
    django.setup()
except Exception:
    # Django может быть уже настроен
    pass

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from home.bot.config import BOT_TOKEN, ADMIN_IDS
from home.bot.handlers import common, order_handlers

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_bot() -> tuple[Bot, Dispatcher]:
    """Создание бота и диспетчера"""
    if not BOT_TOKEN:
        error_msg = (
            "❌ TELEGRAM_BOT_TOKEN не установлен!\n\n"
            "Пожалуйста, установите токен бота одним из способов:\n"
            "1. В файле .env: TELEGRAM_BOT_TOKEN=your_token_here\n"
            "2. В Django settings: TELEGRAM_BOT_TOKEN = 'your_token_here'\n"
            "3. Через командную строку: python manage.py run_bot --token your_token_here\n\n"
            "Для получения токена создайте бота через @BotFather в Telegram."
        )
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    # Проверяем формат токена (должен быть в формате 123456:ABC-DEF...)
    if ':' not in BOT_TOKEN or len(BOT_TOKEN) < 20:
        error_msg = (
            f"❌ Неверный формат токена!\n\n"
            f"Токен должен быть в формате: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz\n"
            f"Текущий токен (первые 10 символов): {BOT_TOKEN[:10]}...\n\n"
            f"Проверьте правильность токена в .env или Django settings."
        )
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    try:
        bot = Bot(
            token=BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
    except Exception as e:
        error_msg = (
            f"❌ Ошибка при создании бота: {str(e)}\n\n"
            f"Проверьте:\n"
            f"1. Правильность токена бота\n"
            f"2. Что токен не содержит лишних пробелов\n"
            f"3. Что бот активен в @BotFather"
        )
        logger.error(error_msg)
        raise ValueError(error_msg) from e
    
    dp = Dispatcher()
    
    # Регистрация роутеров
    dp.include_router(common.router)
    dp.include_router(order_handlers.router)
    
    return bot, dp


async def start_bot():
    """Запуск бота"""
    bot, dp = create_bot()
    
    try:
        # Получаем информацию о боте
        bot_info = await bot.get_me()
        logger.info(f"Бот запущен: @{bot_info.username}")
        
        if ADMIN_IDS:
            logger.info(f"Администраторы: {ADMIN_IDS}")
        
        # Устанавливаем команды бота (появляются в меню при нажатии "/")
        commands = [
            BotCommand(command="start", description="🚀 Начать работу с ботом"),
            BotCommand(command="order", description="📦 Создать новый заказ"),
            BotCommand(command="help", description="ℹ️ Показать справку"),
            BotCommand(command="cancel", description="❌ Отменить текущий заказ"),
        ]
        await bot.set_my_commands(commands)
        logger.info("Команды бота установлены")
        
        # Удаляем старые обновления и запускаем polling
        await dp.start_polling(bot, skip_updates=True)
        
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}", exc_info=True)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(start_bot())
