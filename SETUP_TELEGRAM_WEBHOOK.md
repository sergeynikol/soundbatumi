# Настройка Webhook для Telegram бота

Для работы кнопки "В обработку" необходимо настроить webhook, чтобы Telegram отправлял обновления (включая callback queries) на ваш сервер.

## Шаг 1: Убедитесь, что у вас есть публичный URL

Webhook требует публичный HTTPS URL. Для разработки можно использовать:
- ngrok (https://ngrok.com/)
- localtunnel (https://localtunnel.github.io/www/)
- Или ваш продакшн домен

## Шаг 2: Установите webhook через API Telegram

Выполните следующий запрос (замените `YOUR_BOT_TOKEN` и `YOUR_WEBHOOK_URL`):

```bash
curl -X POST "https://api.telegram.org/botYOUR_BOT_TOKEN/setWebhook?url=https://YOUR_DOMAIN.com/api/telegram-callback/"
```

Или через Python:

```python
import requests

bot_token = "YOUR_BOT_TOKEN"
webhook_url = "https://YOUR_DOMAIN.com/api/telegram-callback/"

response = requests.post(
    f"https://api.telegram.org/bot{bot_token}/setWebhook",
    json={"url": webhook_url}
)

print(response.json())
```

## Шаг 3: Проверьте webhook

```bash
curl "https://api.telegram.org/botYOUR_BOT_TOKEN/getWebhookInfo"
```

## Шаг 4: Для локальной разработки с ngrok

1. Установите ngrok: https://ngrok.com/download
2. Запустите ngrok: `ngrok http 8000`
3. Скопируйте HTTPS URL (например: `https://abc123.ngrok.io`)
4. Установите webhook:
   ```bash
   curl -X POST "https://api.telegram.org/botYOUR_BOT_TOKEN/setWebhook?url=https://abc123.ngrok.io/api/telegram-callback/"
   ```

## Важно

- Webhook URL должен быть HTTPS (для продакшна)
- URL должен быть публично доступен
- Endpoint должен отвечать на POST запросы
- После настройки webhook, polling бот (если запущен) нужно остановить

## Отключение webhook

Если нужно вернуться к polling:

```bash
curl -X POST "https://api.telegram.org/botYOUR_BOT_TOKEN/deleteWebhook"
```
