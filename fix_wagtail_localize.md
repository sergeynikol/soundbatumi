# Исправление ошибки: column "page_revision_id" does not exist

## Проблема
Ошибка возникает при попытке использовать wagtail_localize:
```
ProgrammingError: column "page_revision_id" of relation "wagtail_localize_translationlog" does not exist
```

## Причина
Миграции wagtail_localize не были полностью применены, или таблица была создана без необходимой колонки.

## Быстрое решение

Запустите скрипт исправления:

```bash
cd /home/serg/pythonlerning/sites/code/soundbatumi
python fix_translationlog.py
```

Или через Django shell:

```bash
python manage.py shell < fix_translationlog.py
```

## Решение

### Вариант 1: Применить миграции wagtail_localize (рекомендуется)

```bash
python manage.py migrate wagtail_localize
```

Если это не поможет, попробуйте применить все миграции:

```bash
python manage.py migrate
```

### Вариант 2: Исправить вручную через SQL

Если миграции не помогают, выполните SQL команды напрямую:

```sql
-- Проверьте, существует ли таблица
SELECT EXISTS (
    SELECT FROM information_schema.tables 
    WHERE table_name = 'wagtail_localize_translationlog'
);

-- Если таблица существует, добавьте колонку
ALTER TABLE wagtail_localize_translationlog
ADD COLUMN IF NOT EXISTS page_revision_id INTEGER NULL;

-- Добавьте внешний ключ
ALTER TABLE wagtail_localize_translationlog
ADD CONSTRAINT wagtail_localize_translationlog_page_revision_id_fk
FOREIGN KEY (page_revision_id) 
REFERENCES wagtailcore_revision(id) 
ON DELETE SET NULL;
```

### Вариант 3: Использовать скрипт исправления

Запустите скрипт через Django shell:

```bash
python manage.py shell
```

Затем выполните:

```python
from django.db import connection, transaction

with connection.cursor() as cursor:
    # Проверяем существование колонки
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='wagtail_localize_translationlog' 
        AND column_name='page_revision_id'
    """)
    
    if not cursor.fetchone():
        # Добавляем колонку
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
            
            print("Колонка успешно добавлена!")
    else:
        print("Колонка уже существует.")
```

### Вариант 4: Пересоздать таблицу (крайний случай)

Если ничего не помогает, можно пересоздать таблицу:

```bash
# Удалить таблицу (ОСТОРОЖНО: потеряете данные!)
python manage.py migrate wagtail_localize zero

# Применить миграции заново
python manage.py migrate wagtail_localize
```

## Проверка

После исправления проверьте:

1. Колонка существует:
```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'wagtail_localize_translationlog' 
AND column_name = 'page_revision_id';
```

2. Попробуйте использовать wagtail_localize в админ-панели

## Предотвращение проблемы в будущем

Убедитесь, что все миграции применены:

```bash
python manage.py showmigrations wagtail_localize
```

Все миграции должны быть отмечены как `[X]` (применены).
