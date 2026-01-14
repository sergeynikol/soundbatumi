# Устранение проблем с отправкой заказов в Telegram

## Проверка настроек

1. **Проверьте переменные окружения в `.env`:**
   ```bash
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   TELEGRAM_ADMIN_IDS=5142230994
   ```

2. **Проверьте, что настройки загружаются:**
   ```python
   python manage.py shell
   >>> from django.conf import settings
   >>> print(getattr(settings, 'TELEGRAM_BOT_TOKEN', 'NOT SET'))
   >>> print(getattr(settings, 'TELEGRAM_ADMIN_IDS', 'NOT SET'))
   ```

## Тестирование отправки

### Тест 1: Проверка бота
```python
python manage.py shell
>>> from django.conf import settings
>>> import requests
>>> bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
>>> response = requests.get(f'https://api.telegram.org/bot{bot_token}/getMe')
>>> print(response.json())
```

### Тест 2: Отправка тестового сообщения
```python
python manage.py shell
>>> from django.conf import settings
>>> import requests
>>> bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
>>> admin_id = 5142230994
>>> url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
>>> payload = {'chat_id': admin_id, 'text': 'Тестовое сообщение'}
>>> response = requests.post(url, json=payload)
>>> print(response.json())
```

### Тест 3: Отправка уведомления для существующего заказа
```python
python manage.py shell
>>> from home.models import Order
>>> from home.telegram_notifications import send_order_notification
>>> last_order = Order.objects.order_by('-created_at').first()
>>> result = send_order_notification(last_order)
>>> print(f'Результат: {result}')
```

## Проверка логов

Проверьте логи Django на наличие ошибок:
- В консоли при запуске `python manage.py runserver`
- В файлах логов (если настроены)

Ищите сообщения:
- `✅ Уведомление в Telegram успешно отправлено`
- `⚠️ Не удалось отправить уведомление`
- `❌ Исключение при отправке уведомления`

## Частые проблемы

### 1. Бот не может отправить сообщение
**Ошибка:** `Forbidden: bots can't send messages to bots`
**Решение:** Убедитесь, что `TELEGRAM_ADMIN_IDS` содержит ID пользователя, а не бота.

### 2. Неверный токен
**Ошибка:** `Unauthorized` или `401`
**Решение:** Проверьте правильность токена в `.env` файле.

### 3. Пользователь не начал диалог с ботом
**Ошибка:** `Forbidden: bot was blocked by the user`
**Решение:** Пользователь должен начать диалог с ботом, отправив команду `/start`.

### 4. Функция не вызывается
**Проблема:** Заказ создается, но уведомление не отправляется
**Решение:** 
- Проверьте логи на наличие исключений
- Убедитесь, что код не находится внутри транзакции, которая откатывается

## Ручная отправка уведомлений для старых заказов

Если нужно отправить уведомления для заказов, которые были созданы до настройки бота:

```python
python manage.py shell
>>> from home.models import Order
>>> from home.telegram_notifications import send_order_notification
>>> 
>>> # Отправить для всех заказов
>>> for order in Order.objects.all():
...     send_order_notification(order)
... 
>>> # Или для конкретного заказа
>>> order = Order.objects.get(order_number='ORD-XXXXX')
>>> send_order_notification(order)
```

## Проверка работы в реальном времени

1. Создайте тестовый заказ через веб-интерфейс
2. Следите за логами в консоли
3. Проверьте, пришло ли сообщение в Telegram

Если сообщение не приходит, проверьте:
- Логи на наличие ошибок
- Настройки бота
- Что пользователь начал диалог с ботом
