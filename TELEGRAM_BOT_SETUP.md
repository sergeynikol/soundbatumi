# Настройка Telegram бота для приема заказов

## Установка зависимостей

Убедитесь, что установлены все зависимости:
```bash
pip install -r requirements.txt
```

## Настройка бота

1. Создайте бота через [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте команду `/newbot` и следуйте инструкциям
3. Сохраните токен бота
4. Добавьте в файл `.env`:
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_ADMIN_IDS=your_telegram_user_id1,your_telegram_user_id2
```

Чтобы узнать свой Telegram ID, напишите боту [@userinfobot](https://t.me/userinfobot)

## Запуск бота

### Способ 1: Через Django management команду (рекомендуется)

```bash
python manage.py run_bot
```

### Способ 2: Через Python напрямую

```bash
python home/bot/bot.py
```

### Способ 3: С указанием токена

```bash
python manage.py run_bot --token YOUR_BOT_TOKEN
```

## Запуск бота как сервис (systemd)

Создайте файл `/etc/systemd/system/soundbatumi-bot.service`:

```ini
[Unit]
Description=Sound Batumi Telegram Bot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/home/serg/pythonlerning/sites/code/soundbatumi
Environment="DJANGO_SETTINGS_MODULE=soundbatumi.settings.production"
Environment="TELEGRAM_BOT_TOKEN=your_token_here"
ExecStart=/home/serg/pythonlerning/sites/code/.venv/bin/python manage.py run_bot
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Затем:
```bash
sudo systemctl daemon-reload
sudo systemctl enable soundbatumi-bot
sudo systemctl start soundbatumi-bot
sudo systemctl status soundbatumi-bot
```

## Использование бота

1. Найдите вашего бота в Telegram по username
2. Отправьте команду `/start` или нажмите кнопку "📦 Создать заказ"
3. Следуйте инструкциям бота для создания заказа:
   - Введите имя клиента
   - Укажите номер телефона
   - Введите email (опционально)
   - Укажите адрес доставки
   - Добавьте комментарий (опционально)
   - Добавьте позиции заказа (название, количество, цена)
   - Подтвердите заказ

## Команды бота

- `/start` - Начать работу с ботом
- `/order` - Создать новый заказ
- `/help` - Показать справку
- `/cancel` - Отменить текущий заказ

## Структура проекта

```
home/bot/
├── __init__.py
├── bot.py              # Главный файл бота
├── config.py           # Конфигурация
├── utils.py            # Утилиты (валидация, форматирование)
├── services.py         # Сервисы для работы с Django ORM
├── handlers/           # Обработчики сообщений
│   ├── __init__.py
│   ├── common.py       # Общие команды
│   └── order_handlers.py  # Обработчики заказов
├── keyboards/          # Клавиатуры
│   ├── __init__.py
│   └── order_keyboards.py
└── states/             # FSM состояния
    ├── __init__.py
    └── order_states.py
```

## Особенности

- Бот собирает подробные данные о заказе
- Использует FSM (Finite State Machine) для пошагового сбора данных
- Интегрирован с Django ORM для сохранения заказов в базу данных
- Валидация всех входных данных
- Поддержка нескольких позиций в одном заказе
- Автоматическая генерация номера заказа
- Подтверждение заказа перед сохранением

## Устранение неполадок

### Бот не отвечает

1. Проверьте, что токен бота правильный
2. Убедитесь, что бот запущен (проверьте логи)
3. Проверьте подключение к интернету

### Ошибки при создании заказа

1. Проверьте подключение к базе данных Django
2. Убедитесь, что миграции применены
3. Проверьте логи бота для деталей ошибки

### Бот не запускается

1. Проверьте, что все зависимости установлены
2. Убедитесь, что Django настроен правильно
3. Проверьте, что переменная `DJANGO_SETTINGS_MODULE` установлена
