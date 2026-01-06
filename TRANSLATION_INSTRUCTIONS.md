# Инструкции по созданию файлов переводов

## Установка gettext (если не установлен)

Для Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install gettext
```

Для CentOS/RHEL:
```bash
sudo yum install gettext
```

## Создание файлов переводов

После установки gettext выполните:

```bash
cd /home/serg/pythonlerning/sites/code/soundbatumi
source /home/serg/pythonlerning/sites/code/.venv/bin/activate
python manage.py makemessages -l en -l ru -l ka --ignore=venv --ignore=.venv --ignore=node_modules
```

## Редактирование файлов переводов

Файлы переводов находятся в:
- `locale/en/LC_MESSAGES/django.po` - английский
- `locale/ru/LC_MESSAGES/django.po` - русский
- `locale/ka/LC_MESSAGES/django.po` - грузинский

Отредактируйте файлы `.po`, заполнив переводы для всех строк `msgstr ""`.

## Компиляция переводов

После редактирования файлов `.po` выполните:

```bash
python manage.py compilemessages
```

## Примеры переводов для основных строк

### Русский (ru/LC_MESSAGES/django.po):
```
msgid "Login"
msgstr "Войти"

msgid "Registration"
msgstr "Регистрация"

msgid "Checkout"
msgstr "Оформление заказа"

msgid "Shopping Cart"
msgstr "Корзина заказов"

msgid "Name"
msgstr "Имя"

msgid "Phone"
msgstr "Телефон"

msgid "Delivery Address"
msgstr "Адрес доставки"

msgid "Confirm Order"
msgstr "Подтвердить заказ"

msgid "Cart is empty"
msgstr "Корзина пуста"

msgid "Add to Cart"
msgstr "Добавить в корзину"

msgid "Continue Shopping"
msgstr "Продолжить покупки"

msgid "Total Amount"
msgstr "Итоговая сумма"

msgid "Order"
msgstr "Заказать"

msgid "Quantity"
msgstr "Количество"

msgid "Total"
msgstr "Итого"

msgid "Cancel"
msgstr "Отмена"

msgid "Remove"
msgstr "Удалить"

msgid "Admin"
msgstr "Админ"

msgid "Logout"
msgstr "Выйти"

msgid "Username"
msgstr "Имя пользователя"

msgid "Password"
msgstr "Пароль"

msgid "Confirm Password"
msgstr "Подтверждение пароля"

msgid "Name or Organization"
msgstr "Имя или название организации"

msgid "Contact Information"
msgstr "Контактные данные"

msgid "Phone Number"
msgstr "Номер телефона"

msgid "Messenger Link"
msgstr "Ссылка на мессенджер"

msgid "Select Quantity"
msgstr "Выберите количество"

msgid "Your order #%(order_number)s has been accepted for processing. A manager will contact you shortly."
msgstr "Ваш заказ #%(order_number)s принят на обработку. С вами свяжется менеджер в ближайшее время."

msgid "Order #%(order_number)s has been successfully created! We will contact you shortly."
msgstr "Заказ #%(order_number)s успешно создан! Мы свяжемся с вами в ближайшее время."

msgid "Please enter your name"
msgstr "Пожалуйста, укажите ваше имя"

msgid "Please enter your phone number"
msgstr "Пожалуйста, укажите ваш телефон"

msgid "Please enter delivery address"
msgstr "Пожалуйста, укажите адрес доставки"

msgid "Processing..."
msgstr "Обработка..."

msgid "Discount"
msgstr "Скидка"

msgid "Global discount"
msgstr "Глобальная скидка"

msgid "Only %(quantity)s available"
msgstr "Доступно только %(quantity)s шт."
```

### Грузинский (ka/LC_MESSAGES/django.po):
```
msgid "Login"
msgstr "შესვლა"

msgid "Registration"
msgstr "რეგისტრაცია"

msgid "Checkout"
msgstr "შეკვეთის გაფორმება"

msgid "Shopping Cart"
msgstr "კალათა"

msgid "Name"
msgstr "სახელი"

msgid "Phone"
msgstr "ტელეფონი"

msgid "Delivery Address"
msgstr "მიწოდების მისამართი"

msgid "Confirm Order"
msgstr "შეკვეთის დადასტურება"

msgid "Cart is empty"
msgstr "კალათა ცარიელია"

msgid "Add to Cart"
msgstr "კალათაში დამატება"

msgid "Continue Shopping"
msgstr "შეძენის გაგრძელება"

msgid "Total Amount"
msgstr "საერთო თანხა"

msgid "Order"
msgstr "შეკვეთა"

msgid "Quantity"
msgstr "რაოდენობა"

msgid "Total"
msgstr "სულ"

msgid "Cancel"
msgstr "გაუქმება"

msgid "Remove"
msgstr "წაშლა"

msgid "Admin"
msgstr "ადმინისტრატორი"

msgid "Logout"
msgstr "გასვლა"

msgid "Username"
msgstr "მომხმარებლის სახელი"

msgid "Password"
msgstr "პაროლი"

msgid "Confirm Password"
msgstr "პაროლის დადასტურება"

msgid "Name or Organization"
msgstr "სახელი ან ორგანიზაცია"

msgid "Contact Information"
msgstr "საკონტაქტო ინფორმაცია"

msgid "Phone Number"
msgstr "ტელეფონის ნომერი"

msgid "Messenger Link"
msgstr "მესენჯერის ლინკი"

msgid "Select Quantity"
msgstr "აირჩიეთ რაოდენობა"

msgid "Your order #%(order_number)s has been accepted for processing. A manager will contact you shortly."
msgstr "თქვენი შეკვეთა #%(order_number)s მიღებულია დასამუშავებლად. მენეჯერი დაგიკავშირდებათ მალე."

msgid "Order #%(order_number)s has been successfully created! We will contact you shortly."
msgstr "შეკვეთა #%(order_number)s წარმატებით შექმნილია! ჩვენ დაგიკავშირდებით მალე."

msgid "Please enter your name"
msgstr "გთხოვთ, შეიყვანოთ თქვენი სახელი"

msgid "Please enter your phone number"
msgstr "გთხოვთ, შეიყვანოთ თქვენი ტელეფონის ნომერი"

msgid "Please enter delivery address"
msgstr "გთხოვთ, შეიყვანოთ მიწოდების მისამართი"

msgid "Processing..."
msgstr "მუშავდება..."

msgid "Discount"
msgstr "ფასდაკლება"

msgid "Global discount"
msgstr "გლობალური ფასდაკლება"

msgid "Only %(quantity)s available"
msgstr "მხოლოდ %(quantity)s ცალი ხელმისაწვდომია"
```

### Английский (en/LC_MESSAGES/django.po):
```
msgid "Login"
msgstr "Login"

msgid "Registration"
msgstr "Registration"

msgid "Checkout"
msgstr "Checkout"

msgid "Shopping Cart"
msgstr "Shopping Cart"

msgid "Name"
msgstr "Name"

msgid "Phone"
msgstr "Phone"

msgid "Delivery Address"
msgstr "Delivery Address"

msgid "Confirm Order"
msgstr "Confirm Order"

msgid "Cart is empty"
msgstr "Cart is empty"

msgid "Add to Cart"
msgstr "Add to Cart"

msgid "Continue Shopping"
msgstr "Continue Shopping"

msgid "Total Amount"
msgstr "Total Amount"

msgid "Order"
msgstr "Order"

msgid "Quantity"
msgstr "Quantity"

msgid "Total"
msgstr "Total"

msgid "Cancel"
msgstr "Cancel"

msgid "Remove"
msgstr "Remove"

msgid "Admin"
msgstr "Admin"

msgid "Logout"
msgstr "Logout"

msgid "Username"
msgstr "Username"

msgid "Password"
msgstr "Password"

msgid "Confirm Password"
msgstr "Confirm Password"

msgid "Name or Organization"
msgstr "Name or Organization"

msgid "Contact Information"
msgstr "Contact Information"

msgid "Phone Number"
msgstr "Phone Number"

msgid "Messenger Link"
msgstr "Messenger Link"

msgid "Select Quantity"
msgstr "Select Quantity"

msgid "Your order #%(order_number)s has been accepted for processing. A manager will contact you shortly."
msgstr "Your order #%(order_number)s has been accepted for processing. A manager will contact you shortly."

msgid "Order #%(order_number)s has been successfully created! We will contact you shortly."
msgstr "Order #%(order_number)s has been successfully created! We will contact you shortly."

msgid "Please enter your name"
msgstr "Please enter your name"

msgid "Please enter your phone number"
msgstr "Please enter your phone number"

msgid "Please enter delivery address"
msgstr "Please enter delivery address"

msgid "Processing..."
msgstr "Processing..."

msgid "Discount"
msgstr "Discount"

msgid "Global discount"
msgstr "Global discount"

msgid "Only %(quantity)s available"
msgstr "Only %(quantity)s available"
```

## После компиляции

После выполнения `python manage.py compilemessages` файлы `.mo` будут созданы автоматически, и переводы начнут работать.

## Проверка работы переводов

1. Убедитесь, что в `settings/base.py` правильно настроены языки:
```python
WAGTAIL_CONTENT_LANGUAGES = LANGUAGES = (
    ('en', _('English')),
    ('ka', _('Georgian')),
    ('ru', _('Russian')),
)
```

2. Переключатель языков уже реализован в `blocks/menu.html`

3. После компиляции переводов перезапустите сервер Django
