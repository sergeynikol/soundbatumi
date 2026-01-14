#!/usr/bin/env python
"""
Скрипт для получения ID группы Telegram
"""
import os
import sys
import django
from pathlib import Path

# Настройка Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'soundbatumi.settings.dev')
django.setup()

import requests
from django.conf import settings

def get_group_id():
    """Получает ID группы из последних обновлений бота"""
    bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN не настроен в settings!")
        print("Добавьте TELEGRAM_BOT_TOKEN в .env файл")
        return
    
    print("=" * 60)
    print("Получение ID группы Telegram")
    print("=" * 60)
    print("\n📋 Инструкция:")
    print("1. Добавьте вашего бота в группу")
    print("2. Дайте боту права администратора (опционально, но рекомендуется)")
    print("3. Отправьте любое сообщение в группу")
    print("4. Нажмите Enter здесь, чтобы получить ID группы")
    print("\nИли используйте бота @userinfobot:")
    print("1. Добавьте @userinfobot в вашу группу")
    print("2. Отправьте любое сообщение в группу")
    print("3. Бот ответит с ID группы (отрицательное число)")
    print("\n" + "=" * 60)
    
    input("\nНажмите Enter после того, как отправите сообщение в группу...")
    
    # Получаем последние обновления
    url = f'https://api.telegram.org/bot{bot_token}/getUpdates'
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('ok'):
                updates = data.get('result', [])
                
                if not updates:
                    print("\n❌ Не найдено обновлений.")
                    print("Убедитесь, что:")
                    print("  - Бот добавлен в группу")
                    print("  - Вы отправили сообщение в группу")
                    return
                
                print(f"\n✅ Найдено {len(updates)} обновлений")
                print("\n" + "=" * 60)
                print("Найденные группы:")
                print("=" * 60)
                
                groups_found = {}
                
                for update in updates:
                    message = update.get('message') or update.get('channel_post')
                    if message:
                        chat = message.get('chat', {})
                        chat_type = chat.get('type', '')
                        chat_id = chat.get('id')
                        chat_title = chat.get('title', 'Без названия')
                        
                        if chat_type in ['group', 'supergroup']:
                            if chat_id not in groups_found:
                                groups_found[chat_id] = {
                                    'title': chat_title,
                                    'type': chat_type,
                                    'username': chat.get('username', 'Нет username')
                                }
                
                if groups_found:
                    for chat_id, info in groups_found.items():
                        print(f"\n group: {info['title']}")
                        print(f"   ID: {chat_id}")
                        print(f"   Тип: {info['type']}")
                        if info['username'] != 'Нет username':
                            print(f"   Username: @{info['username']}")
                        print(f"\n   Добавьте в .env:")
                        print(f"   TELEGRAM_GROUP_ID={chat_id}")
                else:
                    print("\n❌ Группы не найдены в обновлениях.")
                    print("Попробуйте:")
                    print("  1. Отправить сообщение в группу снова")
                    print("  2. Использовать бота @userinfobot")
            else:
                print(f"\n❌ Ошибка API: {data.get('description', 'Unknown error')}")
        else:
            print(f"\n❌ HTTP ошибка: {response.status_code}")
            print(response.text)
            
    except requests.RequestException as e:
        print(f"\n❌ Ошибка запроса: {e}")
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")

if __name__ == '__main__':
    get_group_id()
