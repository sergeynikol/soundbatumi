# Настройка OAuth авторизации через Google и Telegram

## Установка зависимостей

Убедитесь, что установлены все зависимости:
```bash
pip install -r requirements.txt
```

## Настройка Google OAuth

1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте новый проект или выберите существующий
3. Включите Google+ API
4. Перейдите в "Credentials" → "Create Credentials" → "OAuth client ID"
5. Выберите тип приложения "Web application"
6. Добавьте авторизованные URI перенаправления:
   - Для разработки: `http://localhost:8000/accounts/google/login/callback/`
   - Для продакшена: `https://yourdomain.com/accounts/google/login/callback/`
7. Сохраните Client ID и Client Secret

8. Добавьте в файл `.env`:
```
GOOGLE_OAUTH2_CLIENT_ID=your_client_id_here
GOOGLE_OAUTH2_SECRET_KEY=your_client_secret_here
```

9. Настройте Social Application одним из способов:

   **Способ 1: Использование management команды (рекомендуется)**
   ```bash
   python manage.py setup_google_oauth
   ```
   Команда автоматически создаст/обновит Social Application используя переменные окружения из `.env`

   **Способ 2: Через админ-панель Django (`/admin/socialaccount/socialapp/`)**
   - Откройте существующую Social Application для Google (уже создана)
   - Обновите:
     - Client id: ваш Client ID
     - Secret key: ваш Client Secret
     - Sites: убедитесь, что выбран ваш сайт
   - Сохраните

   **Способ 3: Через командную строку с параметрами**
   ```bash
   python manage.py setup_google_oauth --client-id YOUR_CLIENT_ID --secret-key YOUR_SECRET_KEY
   ```

## Настройка Telegram Login Widget

1. Создайте бота через [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте команду `/newbot` и следуйте инструкциям
3. Сохраните токен бота
4. Отправьте команду `/setdomain` и укажите домен вашего сайта (например: `yourdomain.com`)
5. Добавьте в файл `.env`:
```
TELEGRAM_BOT_NAME=your_bot_name_here
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

6. Добавьте в `settings/base.py` или `settings/production.py`:
```python
TELEGRAM_BOT_NAME = os.getenv("TELEGRAM_BOT_NAME", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
```

## Применение миграций

После настройки выполните миграции для allauth:
```bash
python manage.py migrate
```

## Проверка работы

1. Перейдите на страницу входа/регистрации
2. Вы должны увидеть кнопки "Continue with Google" и "Continue with Telegram"
3. Попробуйте авторизоваться через оба способа

## Примечания

- Для Telegram Login Widget требуется, чтобы сайт был доступен по HTTPS в продакшене
- Убедитесь, что домен, указанный в BotFather, совпадает с доменом вашего сайта
- Google OAuth требует настройки правильных redirect URI
