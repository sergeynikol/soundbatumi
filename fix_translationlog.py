#!/usr/bin/env python
"""
Скрипт для исправления проблемы с отсутствующей колонкой page_revision_id
в таблице wagtail_localize_translationlog

Использование:
    python fix_translationlog.py

Или через Django shell:
    python manage.py shell
    >>> exec(open('fix_translationlog.py').read())
"""

import os
import sys
import django

# Настройка Django
if 'DJANGO_SETTINGS_MODULE' not in os.environ:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'soundbatumi.settings.base')

try:
    django.setup()
except Exception as e:
    print(f"Ошибка настройки Django: {e}")
    print("Попробуйте запустить через: python manage.py shell < fix_translationlog.py")
    sys.exit(1)

from django.db import connection, transaction
from django.core.management import call_command


def fix_translationlog_table():
    """Добавляет недостающую колонку page_revision_id в таблицу wagtail_localize_translationlog"""
    
    print("Проверка таблицы wagtail_localize_translationlog...")
    
    with connection.cursor() as cursor:
        # Проверяем, существует ли таблица
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'wagtail_localize_translationlog'
            )
        """)
        
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            print("❌ Таблица wagtail_localize_translationlog не существует.")
            print("Применяем миграции wagtail_localize...")
            try:
                call_command('migrate', 'wagtail_localize', verbosity=2)
                print("✅ Миграции применены. Попробуйте снова.")
            except Exception as e:
                print(f"❌ Ошибка при применении миграций: {e}")
                print("Попробуйте вручную: python manage.py migrate wagtail_localize")
            return False
        
        # Проверяем, существует ли колонка
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='wagtail_localize_translationlog' 
            AND column_name='page_revision_id'
        """)
        
        column_exists = cursor.fetchone() is not None
        
        if column_exists:
            print("✅ Колонка page_revision_id уже существует. Ничего делать не нужно.")
            return True
        
        # Проверяем, существует ли таблица wagtailcore_revision
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'wagtailcore_revision'
            )
        """)
        
        revision_table_exists = cursor.fetchone()[0]
        
        if not revision_table_exists:
            print("❌ Таблица wagtailcore_revision не существует.")
            print("Применяем миграции wagtail...")
            try:
                call_command('migrate', 'wagtailcore', verbosity=2)
            except Exception as e:
                print(f"❌ Ошибка: {e}")
            return False
        
        # Добавляем колонку
        print("Добавляем колонку page_revision_id...")
        try:
            with transaction.atomic():
                # Добавляем колонку
                cursor.execute("""
                    ALTER TABLE wagtail_localize_translationlog
                    ADD COLUMN page_revision_id INTEGER NULL
                """)
                
                # Добавляем внешний ключ (если он еще не существует)
                try:
                    cursor.execute("""
                        ALTER TABLE wagtail_localize_translationlog
                        ADD CONSTRAINT wagtail_localize_translationlog_page_revision_id_fk
                        FOREIGN KEY (page_revision_id) 
                        REFERENCES wagtailcore_revision(id) 
                        ON DELETE SET NULL
                    """)
                except Exception as e:
                    if 'already exists' in str(e).lower() or 'duplicate' in str(e).lower():
                        print("⚠️  Внешний ключ уже существует, пропускаем...")
                    else:
                        raise
                
                print("✅ Колонка page_revision_id успешно добавлена!")
                return True
                
        except Exception as e:
            print(f"❌ Ошибка при добавлении колонки: {e}")
            print("\nПопробуйте выполнить SQL вручную:")
            print("""
ALTER TABLE wagtail_localize_translationlog
ADD COLUMN IF NOT EXISTS page_revision_id INTEGER NULL;

ALTER TABLE wagtail_localize_translationlog
ADD CONSTRAINT wagtail_localize_translationlog_page_revision_id_fk
FOREIGN KEY (page_revision_id) 
REFERENCES wagtailcore_revision(id) 
ON DELETE SET NULL;
            """)
            return False


if __name__ == "__main__":
    success = fix_translationlog_table()
    sys.exit(0 if success else 1)
