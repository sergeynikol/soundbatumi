"""
Временный скрипт для исправления проблемы с отсутствующей колонкой page_revision_id
в таблице wagtail_localize_translationlog

Запустите этот скрипт через Django shell:
python manage.py shell < wagtail_localize_fix_migration.py

Или выполните команды вручную через manage.py shell
"""

from django.db import connection, transaction

def fix_translationlog_table():
    """Добавляет недостающую колонку page_revision_id в таблицу wagtail_localize_translationlog"""
    
    with connection.cursor() as cursor:
        # Проверяем, существует ли колонка
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='wagtail_localize_translationlog' 
            AND column_name='page_revision_id'
        """)
        
        if cursor.fetchone():
            print("Колонка page_revision_id уже существует. Ничего делать не нужно.")
            return
        
        # Проверяем, существует ли таблица
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'wagtail_localize_translationlog'
            )
        """)
        
        if not cursor.fetchone()[0]:
            print("Таблица wagtail_localize_translationlog не существует.")
            print("Необходимо применить миграции wagtail_localize:")
            print("python manage.py migrate wagtail_localize")
            return
        
        # Добавляем колонку
        print("Добавляем колонку page_revision_id...")
        with transaction.atomic():
            cursor.execute("""
                ALTER TABLE wagtail_localize_translationlog
                ADD COLUMN page_revision_id INTEGER NULL
            """)
            
            # Добавляем внешний ключ
            cursor.execute("""
                ALTER TABLE wagtail_localize_translationlog
                ADD CONSTRAINT wagtail_localize_translationlog_page_revision_id_fk
                FOREIGN KEY (page_revision_id) 
                REFERENCES wagtailcore_revision(id) 
                ON DELETE SET NULL
            """)
            
            print("Колонка page_revision_id успешно добавлена!")

if __name__ == "__main__":
    fix_translationlog_table()
