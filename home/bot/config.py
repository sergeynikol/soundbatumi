"""
Конфигурация для Telegram бота
"""
import os

# Пытаемся получить токен из переменных окружения или Django settings
BOT_TOKEN = None

# Сначала пытаемся из переменных окружения
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')

# Если не нашли, пытаемся из Django settings
if not BOT_TOKEN:
    try:
        from django.conf import settings
        BOT_TOKEN = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
    except Exception:
        pass

# Убираем пробелы и проверяем, что токен не пустой
if BOT_TOKEN:
    BOT_TOKEN = BOT_TOKEN.strip()

# ID администраторов (список через запятую в .env)
ADMIN_IDS = []

# Сначала из переменных окружения
admin_ids_str = os.getenv('TELEGRAM_ADMIN_IDS', '')
if not admin_ids_str:
    # Пытаемся из Django settings
    try:
        from django.conf import settings
        admin_ids_str = getattr(settings, 'TELEGRAM_ADMIN_IDS', '')
    except Exception:
        pass

if admin_ids_str:
    ADMIN_IDS = [
        int(admin_id.strip()) 
        for admin_id in admin_ids_str.split(',') 
        if admin_id.strip().isdigit()
    ]

# Язык по умолчанию
DEFAULT_LANGUAGE = 'ru'
