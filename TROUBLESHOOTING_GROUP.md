# Устранение проблем с отправкой сообщений в группу

## Проверка настроек

1. **Проверьте, что `TELEGRAM_GROUP_ID` настроен в `.env`:**
   ```bash
   TELEGRAM_GROUP_ID=-1003507476034
   ```

2. **Проверьте настройки через Django shell:**
   ```python
   python manage.py shell
   >>> from django.conf import settings
   >>> print(getattr(settings, 'TELEGRAM_GROUP_ID', 'NOT SET'))
   ```

## Тестирование отправки

### Тест 1: Проверка бота и группы
```python
python manage.py shell
>>> import requests
>>> from django.conf import settings
>>> bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
>>> group_id = getattr(settings, 'TELEGRAM_GROUP_ID', None)
>>> 
>>> # Проверка бота
>>> bot_info = requests.get(f'https://api.telegram.org/bot{bot_token}/getMe').json()
>>> print(bot_info)
>>> 
>>> # Тестовая отправка
>>> response = requests.post(
...     f'https://api.telegram.org/bot{bot_token}/sendMessage',
...     json={'chat_id': group_id, 'text': 'Тест'}
... )
>>> print(response.json())
```

### Тест 2: Отправка уведомления для существующего заказа
```python
python manage.py shell
>>> from home.models import Order
>>> from home.telegram_notifications import send_order_notification
>>> 
>>> last_order = Order.objects.order_by('-created_at').first()
>>> result = send_order_notification(last_order)
>>> print(f'Результат: {result}')
```

## Частые проблемы

### 1. Бот не добавлен в группу
**Ошибка:** `chat not found` или `chat_id is empty`
**Решение:** 
- Добавьте бота в группу
- Дайте боту права администратора (рекомендуется)

### 2. Бот не имеет прав на отправку сообщений
**Ошибка:** `not enough rights to send messages`
**Решение:** 
- Дайте боту права администратора в группе
- Или убедитесь, что бот может отправлять сообщения

### 3. Группа заблокировала бота
**Ошибка:** `bot was blocked by the user`
**Решение:** 
- Удалите бота из группы
- Добавьте снова

### 4. Неправильный ID группы
**Ошибка:** `chat not found`
**Решение:** 
- Проверьте правильность ID группы
- Используйте бота @userinfobot для получения правильного ID

### 5. Группа является каналом
**Проблема:** Боты не могут отправлять сообщения в каналы напрямую
**Решение:** 
- Используйте группу, а не канал
- Или настройте бота как администратора канала

## Проверка логов

При создании заказа проверьте логи Django на наличие сообщений:
- `✅ Уведомление в Telegram успешно отправлено`
- `⚠️ Не удалось отправить уведомление`
- `❌ Исключение при отправке уведомления`

## Ручная отправка для старых заказов

Если нужно отправить уведомления для заказов, которые были созданы до настройки группы:

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
2. Следите за логами в консоли Django
3. Проверьте, пришло ли сообщение в группу

Если сообщение не приходит, проверьте:
- Логи на наличие ошибок
- Настройки бота
- Что бот добавлен в группу и имеет права
