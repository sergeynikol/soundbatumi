from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.utils.translation import gettext
from django.db import transaction
from decimal import Decimal, InvalidOperation
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json
import random
import hashlib
import hmac
import time
import requests
import logging
from datetime import datetime
from .models import Order, OrderItem, UserProfile
from .telegram_notifications import format_order_message


@require_http_methods(["GET", "POST"])
def user_login(request):
    """Представление для авторизации пользователя"""
    # Если пользователь уже авторизован, перенаправляем
    if request.user.is_authenticated:
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if is_ajax:
            return JsonResponse({'success': True, 'redirect': '/'})
        return redirect('/')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        next_url = request.POST.get('next', request.GET.get('next', '/'))
        
        # Проверяем, это AJAX запрос из модального окна или обычная отправка формы
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        # Валидация входных данных
        if not username:
            error_msg = gettext('Please enter your username.')
            if is_ajax:
                return JsonResponse({'success': False, 'error': error_msg}, status=400)
            messages.error(request, error_msg)
            return render(request, 'auth/login.html')
        
        if not password:
            error_msg = gettext('Please enter your password.')
            if is_ajax:
                return JsonResponse({'success': False, 'error': error_msg}, status=400)
            messages.error(request, error_msg)
            return render(request, 'auth/login.html')
        
        # Аутентификация пользователя
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                welcome_msg = gettext('Welcome, %(username)s!') % {'username': user.username}
                messages.success(request, welcome_msg)
                
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'redirect': next_url,
                        'message': welcome_msg
                    })
                
                return redirect(next_url)
            else:
                error_msg = gettext('Your account is deactivated. Please contact administrator.')
                if is_ajax:
                    return JsonResponse({'success': False, 'error': error_msg}, status=403)
                messages.error(request, error_msg)
        else:
            error_msg = gettext('Invalid username or password.')
            if is_ajax:
                return JsonResponse({'success': False, 'error': error_msg}, status=400)
            messages.error(request, error_msg)
    
    # Если это GET запрос или POST с ошибкой (не AJAX), показываем страницу логина
    return render(request, 'auth/login.html')


@require_http_methods(["POST", "GET"])
def user_logout(request):
    """Представление для выхода пользователя"""
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, gettext('You have successfully logged out.'))
    return redirect('/')


@require_http_methods(["POST"])
def create_order(request):
    """API endpoint для создания заказа из корзины"""
    try:
        # Проверяем, что это JSON запрос (может быть с charset)
        content_type = request.content_type or ''
        if 'application/json' not in content_type:
            return JsonResponse({
                'success': False, 
                'error': gettext('Invalid Content-Type: %(content_type)s. Expected application/json') % {'content_type': content_type}
            }, status=400)
        
        # Парсим JSON данные
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError as e:
            return JsonResponse({
                'success': False, 
                'error': gettext('Invalid JSON format: %(error)s') % {'error': str(e)}
            }, status=400)
        
        # Получаем данные заказа
        delivery_address = (data.get('delivery_address') or '').strip()
        customer_name = (data.get('customer_name') or '').strip()
        customer_phone = (data.get('customer_phone') or '').strip()
        customer_email = (data.get('customer_email') or '').strip()
        customer_comment = (data.get('customer_comment') or '').strip()
        installation_date = (data.get('installation_date') or '').strip()
        installation_time = (data.get('installation_time') or '').strip()
        cart_items = data.get('cart_items', [])
        
        # Валидация данных заказа
        validation_errors = []
        
        if not delivery_address:
            validation_errors.append(gettext('Delivery address is required'))
        elif len(delivery_address) > 1000:
            validation_errors.append(gettext('Delivery address must not exceed 1000 characters'))
        
        if not customer_name:
            validation_errors.append(gettext('Customer name is required'))
        elif len(customer_name) > 255:
            validation_errors.append(gettext('Customer name must not exceed 255 characters'))
        
        if not customer_phone:
            validation_errors.append(gettext('Phone number is required'))
        elif len(customer_phone) > 50:
            validation_errors.append(gettext('Phone number must not exceed 50 characters'))
        
        if customer_email:
            if len(customer_email) > 254:
                validation_errors.append(gettext('Email must not exceed 254 characters'))
            else:
                from django.core.validators import validate_email
                try:
                    validate_email(customer_email)
                except ValidationError:
                    validation_errors.append(gettext('Invalid email format'))
        
        if customer_comment and len(customer_comment) > 2000:
            validation_errors.append(gettext('Comment must not exceed 2000 characters'))
        
        # Валидация даты и времени монтажа (обязательные поля)
        if not installation_date:
            validation_errors.append(gettext('Installation date is required'))
        
        if not installation_time:
            validation_errors.append(gettext('Installation time is required'))
        
        installation_date_obj = None
        installation_time_obj = None
        
        if installation_date:
            try:
                from datetime import datetime as dt
                installation_date_obj = dt.strptime(installation_date, '%Y-%m-%d').date()
                # Проверяем, что дата не в прошлом
                from django.utils import timezone
                now = timezone.now()
                today = now.date()
                current_time = now.time()
                
                if installation_date_obj < today:
                    validation_errors.append(gettext('Installation date cannot be in the past'))
                elif installation_date_obj == today and installation_time:
                    # Если выбрана сегодняшняя дата, проверяем, что время не в прошлом
                    try:
                        installation_time_obj = dt.strptime(installation_time, '%H:%M').time()
                        if installation_time_obj < current_time:
                            validation_errors.append(
                                gettext('Installation time cannot be in the past for today')
                            )
                    except ValueError:
                        pass  # Ошибка формата времени будет обработана ниже
            except ValueError:
                validation_errors.append(gettext('Invalid installation date format'))
        
        if installation_time and not installation_time_obj:
            try:
                from datetime import datetime as dt
                installation_time_obj = dt.strptime(installation_time, '%H:%M').time()
            except ValueError:
                validation_errors.append(gettext('Invalid installation time format'))
        
        if not cart_items:
            validation_errors.append(gettext('Cart is empty'))
        elif not isinstance(cart_items, list):
            validation_errors.append(gettext('Invalid cart data format'))
        
        if validation_errors:
            return JsonResponse({
                'success': False,
                'error': '; '.join(validation_errors)
            }, status=400)
        
        # Используем транзакцию для атомарности операции
        with transaction.atomic():
            # Генерируем уникальный номер заказа
            # Используем timestamp + случайное число для избежания конфликтов
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            random_suffix = random.randint(1000, 9999)
            order_number = f"ORD-{timestamp}-{random_suffix}"
            
            # Проверяем уникальность (маловероятно, но на всякий случай)
            while Order.objects.filter(order_number=order_number).exists():
                random_suffix = random.randint(1000, 9999)
                order_number = f"ORD-{timestamp}-{random_suffix}"
            
            # Создаем заказ
            # Если пользователь зарегистрирован, связываем заказ с ним
            order = Order.objects.create(
                order_number=order_number,
                delivery_address=delivery_address,
                customer_name=customer_name,
                customer_phone=customer_phone,
                customer_email=customer_email if customer_email else None,
                customer_comment=customer_comment if customer_comment else None,
                installation_date=installation_date_obj,
                installation_time=installation_time_obj,
                status='pending',
                user=request.user if request.user.is_authenticated else None
            )
            
            # Создаем позиции заказа
            total_amount = Decimal('0.00')
            for item in cart_items:
                try:
                    # Получаем и конвертируем цену с правильной обработкой
                    price_value = item.get('price', 0)
                    if price_value is None:
                        price_value = 0
                    elif isinstance(price_value, str):
                        # Убираем пробелы и проверяем, что строка не пустая
                        price_value = price_value.strip()
                        if not price_value:
                            price_value = 0
                        else:
                            # Заменяем запятую на точку для поддержки
                            # европейского формата чисел (570,00 -> 570.00)
                            price_value = price_value.replace(',', '.')
                            # Убираем пробелы, которые могут быть
                            # разделителями тысяч
                            price_value = price_value.replace(' ', '')
                            # Пытаемся преобразовать строку в float, затем в Decimal
                            try:
                                price_value = float(price_value)
                            except (ValueError, TypeError):
                                raise ValueError(
                                    gettext('Invalid price format: %(price)s') %
                                    {'price': item.get('price', 0)}
                                )
                    elif not isinstance(price_value, (int, float, Decimal)):
                        raise ValueError(
                            gettext('Price must be a number, got: %(type)s') %
                            {'type': type(price_value).__name__}
                        )
                    
                    unit_price = Decimal(str(price_value))
                    quantity_value = item.get('quantity', 1)
                    if quantity_value is None:
                        quantity_value = 1
                    elif isinstance(quantity_value, str):
                        quantity_value = quantity_value.strip()
                        if not quantity_value:
                            quantity_value = 1
                    quantity = int(quantity_value)
                    
                    if quantity <= 0:
                        raise ValueError(gettext('Item quantity must be greater than 0'))
                    
                    if unit_price < 0:
                        raise ValueError(gettext('Item price cannot be negative'))
                    
                    total_price = unit_price * quantity
                    total_amount += total_price
                    
                    OrderItem.objects.create(
                        order=order,
                        equipment_name=item.get('name', gettext('No name'))[:255],
                        equipment_id=item.get('id', '')[:255] if item.get('id') else '',
                        quantity=quantity,
                        unit_price=unit_price,
                        total_price=total_price,
                        equipment_image=item.get('image', '')[:200] if item.get('image') else ''
                    )
                except (ValueError, InvalidOperation, TypeError) as e:
                    # Откатываем транзакцию при ошибке
                    raise ValueError(gettext('Invalid item data format: %(error)s') % {'error': str(e)})
            
            # Обновляем общую сумму заказа
            order.total_amount = total_amount
            order.save()
            
            # Логируем успешное создание заказа
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f'Order created successfully: {order_number}, User: {request.user.username if request.user.is_authenticated else "Anonymous"}, Items: {len(cart_items)}, Total: {total_amount}')
            
            # Отправляем уведомление в Telegram
            # ВАЖНО: Делаем это ПОСЛЕ сохранения заказа в БД, чтобы order.id был доступен
            try:
                logger.info(f'Попытка отправить уведомление в Telegram для заказа {order_number} (ID: {order.id})')
                from .telegram_notifications import send_order_notification
                result = send_order_notification(order)
                if result:
                    logger.info(
                        f'✅ Уведомление в Telegram успешно отправлено для заказа {order_number}'
                    )
                else:
                    logger.warning(
                        f'⚠️ Не удалось отправить уведомление в Telegram для заказа {order_number}. '
                        f'Проверьте настройки TELEGRAM_BOT_TOKEN и TELEGRAM_ADMIN_IDS.'
                    )
            except Exception as e:
                # Логируем ошибку, но не прерываем создание заказа
                logger.error(
                    f'❌ Исключение при отправке уведомления в Telegram '
                    f'для заказа {order_number}: {e}',
                    exc_info=True
                )
        
        # Формируем сообщение в зависимости от того, зарегистрирован ли пользователь
        if request.user.is_authenticated:
            message = gettext('Your order #%(order_number)s has been accepted for processing. A manager will contact you shortly.') % {'order_number': order_number}
        else:
            message = gettext('Order #%(order_number)s has been successfully created! We will contact you shortly.') % {'order_number': order_number}
        
        return JsonResponse({
            'success': True,
            'order_number': order_number,
            'message': message,
            'is_authenticated': request.user.is_authenticated
        })
        
    except ValueError as e:
        # Ошибки валидации данных товаров
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f'Order validation error: {str(e)}')
        return JsonResponse({
            'success': False, 
            'error': str(e)
        }, status=400)
    except Exception as e:
        # Логируем ошибку для отладки
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Error creating order: {str(e)}', exc_info=True)
        
        # Возвращаем понятное сообщение об ошибке
        error_message = gettext('Error creating order: %(error)s') % {'error': str(e)}
        return JsonResponse({
            'success': False, 
            'error': error_message
        }, status=500)


@require_http_methods(["GET", "POST"])
def user_register(request):
    """Представление для регистрации нового пользователя"""
    if request.user.is_authenticated:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'redirect': '/'})
        return redirect('/')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        password_confirm = request.POST.get('password_confirm', '').strip()
        name_or_organization = request.POST.get('name_or_organization', '').strip()
        contact_type = request.POST.get('contact_type', 'phone')
        phone = request.POST.get('phone', '').strip()
        messenger_link = request.POST.get('messenger_link', '').strip()
        
        # Проверяем, это AJAX запрос из модального окна или обычная отправка формы
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        # Валидация
        errors = []
        
        # Валидация имени пользователя
        if not username:
            errors.append(gettext('Username is required'))
        elif len(username) < 3:
            errors.append(gettext('Username must contain at least 3 characters'))
        elif len(username) > 150:
            errors.append(gettext('Username must not exceed 150 characters'))
        elif not username.replace('_', '').replace('.', '').replace('@', '').replace('+', '').replace('-', '').isalnum():
            errors.append(gettext('Username can only contain letters, numbers and symbols: @/./+/-/_'))
        elif User.objects.filter(username=username).exists():
            errors.append(gettext('A user with this username already exists'))
        
        # Валидация пароля
        if not password:
            errors.append(gettext('Password is required'))
        elif len(password) < 8:
            errors.append(gettext('Password must contain at least 8 characters'))
        elif len(password) > 128:
            errors.append(gettext('Password must not exceed 128 characters'))
        
        if password != password_confirm:
            errors.append(gettext('Passwords do not match'))
        
        # Валидация имени/организации
        if not name_or_organization:
            errors.append(gettext('Name or organization is required'))
        elif len(name_or_organization) > 255:
            errors.append(gettext('Organization name must not exceed 255 characters'))
        
        # Проверка контактных данных
        if contact_type == 'phone':
            if not phone:
                errors.append(gettext('Phone number is required'))
            elif len(phone) > 50:
                errors.append(gettext('Phone number must not exceed 50 characters'))
            messenger_link = None
        elif contact_type == 'messenger':
            if not messenger_link:
                errors.append(gettext('Messenger link is required'))
            elif len(messenger_link) > 200:
                errors.append(gettext('Messenger link must not exceed 200 characters'))
            elif not messenger_link.startswith(('http://', 'https://')):
                errors.append(gettext('Messenger link must start with http:// or https://'))
            phone = None
        else:
            errors.append(gettext('Either phone number or messenger link must be provided'))
        
        if errors:
            error_msg = '; '.join(errors)
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'error': error_msg
                }, status=400)
            messages.error(request, error_msg)
            return render(request, 'auth/login.html')
        
        # Создаем пользователя
        try:
            user = User.objects.create_user(
                username=username,
                password=password
            )
            
            # Создаем профиль пользователя
            try:
                UserProfile.objects.create(
                    user=user,
                    phone=phone,
                    messenger_link=messenger_link,
                    name_or_organization=name_or_organization
                )
            except ValidationError as e:
                # Если валидация профиля не прошла, удаляем пользователя
                user.delete()
                raise e
            
            # Автоматически входим пользователя
            login(request, user)
            welcome_msg = gettext('Welcome, %(username)s! Registration successful.') % {'username': user.username}
            messages.success(request, welcome_msg)
            
            if is_ajax:
                success_msg = gettext('Registration successful! Welcome, %(username)s!') % {'username': user.username}
                return JsonResponse({
                    'success': True,
                    'redirect': '/',
                    'message': success_msg
                })
            
            return redirect('/')
            
        except ValidationError as e:
            error_msg = gettext('Validation error: %(error)s') % {'error': '; '.join(e.messages) if hasattr(e, "messages") else str(e)}
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'error': error_msg
                }, status=400)
            messages.error(request, error_msg)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Error during registration: {str(e)}', exc_info=True)
            
            error_msg = gettext('An error occurred during registration. Please try again.')
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'error': error_msg
                }, status=500)
            messages.error(request, error_msg)
    
    # Если это GET запрос, показываем страницу логина (регистрация через модальное окно)
    return render(request, 'auth/login.html')


@require_http_methods(["POST"])
@csrf_exempt
def telegram_login(request):
    """
    Обработка авторизации через Telegram Login Widget
    Telegram отправляет данные через POST запрос после успешной авторизации
    """
    try:
        data = json.loads(request.body) if request.content_type == 'application/json' else request.POST

        telegram_id = data.get('id')
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        username = data.get('username', '')
        auth_date = data.get('auth_date')
        hash_value = data.get('hash')

        bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)

        if not bot_token:
            return JsonResponse({
                'success': False,
                'error': gettext('Telegram authentication is not configured')
            }, status=500)

        # Проверка подписи
        if hash_value:
            data_check_string = []
            for key in sorted(data.keys()):
                if key != 'hash':
                    data_check_string.append(f"{key}={data[key]}")
            check_string = '\n'.join(data_check_string)

            secret_key = hashlib.sha256(bot_token.encode()).digest()
            calculated_hash = hmac.new(
                secret_key,
                check_string.encode(),
                hashlib.sha256
            ).hexdigest()

            if calculated_hash != hash_value:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Telegram login: Invalid hash. Calculated: {calculated_hash}, Received: {hash_value}, Data: {data}")
                return JsonResponse({
                    'success': False,
                    'error': gettext('Invalid authentication data')
                }, status=400)

        if auth_date:
            current_time = int(time.time())
            if current_time - int(auth_date) > 86400:  # 24 hours
                return JsonResponse({
                    'success': False,
                    'error': gettext('Authentication data expired')
                }, status=400)

        if not telegram_id:
            return JsonResponse({
                'success': False,
                'error': gettext('Telegram ID is required')
            }, status=400)

        django_username = f'telegram_{telegram_id}'
        if username:
            django_username = f'tg_{username}'

        user = None
        try:
            user = User.objects.get(username=django_username)
        except User.DoesNotExist:
            import secrets
            random_password = secrets.token_urlsafe(32)
            full_name = f"{first_name} {last_name}".strip() or username or f"Telegram User {telegram_id}"

            user = User.objects.create_user(
                username=django_username,
                password=random_password,
                first_name=first_name,
                last_name=last_name or '',
                email='',
            )
            UserProfile.objects.create(
                user=user,
                name_or_organization=full_name,
                messenger_link=f'https://t.me/{username}' if username else None,
            )

        login(request, user)

        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        if is_ajax:
            return JsonResponse({
                'success': True,
                'redirect': '/',
                'message': gettext('Successfully logged in with Telegram!')
            })

        messages.success(request, gettext('Successfully logged in with Telegram!'))
        return redirect('/')

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': gettext('Invalid JSON data')
        }, status=400)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Error during Telegram login: {str(e)}', exc_info=True)

        return JsonResponse({
            'success': False,
            'error': gettext('An error occurred during Telegram login.')
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def telegram_callback(request):
    """
    Обработка callback запросов от Telegram бота (webhook)
    Обрабатывает нажатия на inline кнопки в сообщениях о заказах
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Логируем сырые данные для диагностики
        raw_body = request.body.decode('utf-8')
        logger.info(f'Received raw webhook data: {raw_body[:500]}')  # Первые 500 символов
        
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError as e:
            logger.error(f'Invalid JSON in webhook: {e}, body: {raw_body[:200]}')
            return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)
        
        logger.info(f'Parsed webhook data: {json.dumps(data, indent=2, ensure_ascii=False)[:1000]}')
        
        # Telegram отправляет callback_query в объекте update
        # Формат: {"update_id": 123, "callback_query": {...}}
        callback_query = data.get('callback_query')
        
        if not callback_query:
            # Если это не callback_query, возвращаем ok для других типов обновлений
            update_type = list(data.keys())[0] if data else 'empty'
            logger.info(f'No callback_query in update (type: {update_type}), ignoring. Update keys: {list(data.keys())}')
            return JsonResponse({'ok': True})
        
        callback_data = callback_query.get('data', '')
        message = callback_query.get('message', {})
        from_user = callback_query.get('from', {})
        
        # Проверяем формат callback_data: process_order_{order_id}
        if not callback_data.startswith('process_order_'):
            logger.warning(f'Invalid callback data: {callback_data}')
            return JsonResponse({'ok': True})  # Отвечаем ok, чтобы Telegram не повторял запрос
        
        # Извлекаем ID заказа
        try:
            order_id = int(callback_data.replace('process_order_', ''))
        except ValueError:
            logger.error(f'Invalid order ID in callback_data: {callback_data}')
            return JsonResponse({'ok': True})
        
        # Получаем заказ из базы данных
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            logger.error(f'Order {order_id} not found')
            return JsonResponse({'ok': True})
        
        # Получаем настройки бота
        bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        if not bot_token:
            logger.error('TELEGRAM_BOT_TOKEN not configured')
            return JsonResponse({'ok': False, 'error': 'Bot token not configured'}, status=500)
        
        # Получаем информацию о сообщении
        chat_id = message.get('chat', {}).get('id')
        message_id = message.get('message_id')
        
        # Получаем ID пользователя, который нажал кнопку
        user_id = from_user.get('id')
        user_first_name = from_user.get('first_name', '')
        callback_query_id = callback_query.get('id')
        
        if not chat_id or not message_id or not user_id or not callback_query_id:
            logger.error(
                f'Missing required data: chat_id={chat_id}, message_id={message_id}, '
                f'user_id={user_id}, callback_query_id={callback_query_id}. '
                f'Full callback_query: {json.dumps(callback_query, indent=2, ensure_ascii=False)[:500]}'
            )
            return JsonResponse({'ok': True})
        
        # 1. Отвечаем на callback query сразу (чтобы убрать индикатор загрузки)
        answer_url = f'https://api.telegram.org/bot{bot_token}/answerCallbackQuery'
        answer_payload = {
            'callback_query_id': callback_query_id,
            'text': f'Заказ #{order.order_number} взят в обработку',
            'show_alert': False
        }
        logger.info(f'Отвечаем на callback query: callback_query_id={callback_query_id}, order={order.order_number}')
        answer_response = requests.post(answer_url, json=answer_payload, timeout=10)
        if answer_response.status_code == 200:
            answer_result = answer_response.json()
            if answer_result.get('ok'):
                logger.info(f'✅ Ответ на callback query успешно отправлен для заказа {order.order_number}')
            else:
                error_desc = answer_result.get('description', 'Unknown error')
                logger.warning(f'⚠️ Не удалось ответить на callback query для заказа {order.order_number}: {error_desc}')
        else:
            logger.warning(f'⚠️ HTTP ошибка при ответе на callback query для заказа {order.order_number}: {answer_response.status_code}')
        
        # 2. Удаляем оригинальное сообщение из группы ПЕРВЫМ ДЕЛОМ
        # Это важно, чтобы сразу убрать сообщение с кнопкой
        logger.info(f'Попытка удалить сообщение: chat_id={chat_id}, message_id={message_id}')
        
        delete_url = f'https://api.telegram.org/bot{bot_token}/deleteMessage'
        delete_payload = {
            'chat_id': chat_id,  # ID группы
            'message_id': message_id
        }
        
        delete_response = requests.post(delete_url, json=delete_payload, timeout=10)
        delete_success = False
        
        if delete_response.status_code == 200:
            delete_result = delete_response.json()
            if delete_result.get('ok'):
                delete_success = True
                logger.info(f'✅ Сообщение о заказе {order.order_number} удалено из группы {chat_id}')
            else:
                error_desc = delete_result.get('description', 'Unknown error')
                logger.error(f'❌ Ошибка при удалении сообщения из группы для заказа {order.order_number}: {error_desc}')
                # Специальная обработка для разных типов ошибок
                if 'not enough rights' in error_desc.lower() or 'message can\'t be deleted' in error_desc.lower():
                    logger.warning(
                        f'⚠️ Бот не имеет прав на удаление сообщений в группе {chat_id}. '
                        f'Дайте боту права администратора или права на удаление сообщений.'
                    )
                elif 'message to delete not found' in error_desc.lower():
                    logger.info(f'ℹ️ Сообщение {message_id} уже удалено из группы {chat_id} (это нормально)')
                    delete_success = True  # Считаем успешным, если сообщение уже удалено
                elif 'bad request' in error_desc.lower():
                    logger.warning(f'⚠️ Неверный запрос на удаление. Проверьте chat_id и message_id.')
        else:
            try:
                error_data = delete_response.json()
                error_desc = error_data.get('description', f'HTTP {delete_response.status_code}')
            except:
                error_desc = f'HTTP {delete_response.status_code}: {delete_response.text}'
            logger.error(f'❌ HTTP ошибка при удалении сообщения из группы для заказа {order.order_number}: {error_desc}')
        
        # 3. Отправляем сообщение в группу о том, кто взял заказ (после удаления)
        # Это сообщение заменит удаленное сообщение
        try:
            group_notification_url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
            
            # Формируем текст уведомления для группы
            group_notification_text = (
                f'✅ <b>Заказ #{order.order_number} взят в обработку</b>\n\n'
                f'👨‍💼 <b>Обрабатывает:</b> {user_first_name}'
            )
            if from_user.get('username'):
                group_notification_text += f' (@{from_user.get("username")})'
            
            group_notification_payload = {
                'chat_id': chat_id,  # ID группы
                'text': group_notification_text,
                'parse_mode': 'HTML'
            }
            
            logger.info(f'Отправка уведомления в группу {chat_id} о взятии заказа {order.order_number}')
            
            group_notification_response = requests.post(
                group_notification_url, 
                json=group_notification_payload, 
                timeout=10
            )
            
            if group_notification_response.status_code == 200:
                group_notification_result = group_notification_response.json()
                if group_notification_result.get('ok'):
                    logger.info(f'✅ Уведомление о взятии заказа {order.order_number} в обработку отправлено в группу {chat_id}')
                else:
                    error_desc = group_notification_result.get('description', 'Unknown error')
                    logger.warning(f'⚠️ Не удалось отправить уведомление в группу для заказа {order.order_number}: {error_desc}')
            else:
                try:
                    error_data = group_notification_response.json()
                    error_desc = error_data.get('description', f'HTTP {group_notification_response.status_code}')
                except:
                    error_desc = f'HTTP {group_notification_response.status_code}: {group_notification_response.text}'
                logger.warning(f'⚠️ HTTP ошибка при отправке уведомления в группу для заказа {order.order_number}: {error_desc}')
        except Exception as e:
            logger.error(f'Ошибка при отправке уведомления в группу: {e}', exc_info=True)
        
        # 4. Отправляем сообщение о заказе пользователю в личные сообщения от бота
        # Формируем сообщение о заказе
        try:
            order_message = format_order_message(order)
        except Exception as e:
            logger.error(f'Ошибка при формировании сообщения о заказе: {e}')
            order_message = (
                f'🆕 <b>Новый заказ #{order.order_number}</b>\n\n'
                f'👤 <b>Клиент:</b> {order.customer_name}\n'
                f'📱 <b>Телефон:</b> {order.customer_phone}\n'
                f'📍 <b>Адрес:</b> {order.delivery_address}\n'
                f'💰 <b>Сумма:</b> {order.total_amount:.2f} ₾'
            )
        
        # Отправляем сообщение пользователю от бота
        send_url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
        send_payload = {
            'chat_id': user_id,
            'text': order_message,
            'parse_mode': 'HTML'
        }
        
        logger.info(f'Попытка отправить сообщение о заказе пользователю: chat_id={user_id}, user={user_first_name}')
        
        send_response = requests.post(send_url, json=send_payload, timeout=10)
        
        if send_response.status_code == 200:
            send_result = send_response.json()
            if send_result.get('ok'):
                logger.info(f'✅ Сообщение о заказе {order.order_number} отправлено пользователю {user_id} ({user_first_name}) от бота')
            else:
                error_desc = send_result.get('description', 'Unknown error')
                logger.error(f'❌ Не удалось отправить сообщение пользователю {user_id} для заказа {order.order_number}: {error_desc}')
                # Если пользователь не начал диалог, это нормально - просто логируем
                if 'bot was blocked' in error_desc.lower() or 'chat not found' in error_desc.lower():
                    logger.warning(
                        f'⚠️ Пользователь {user_id} ({user_first_name}) не начал диалог с ботом. '
                        f'Попросите пользователя написать боту /start'
                    )
        else:
            try:
                error_data = send_response.json()
                error_desc = error_data.get('description', f'HTTP {send_response.status_code}')
            except:
                error_desc = f'HTTP {send_response.status_code}: {send_response.text}'
            logger.error(f'❌ HTTP ошибка при отправке сообщения пользователю {user_id} для заказа {order.order_number}: {error_desc}')
        
        # 6. Обновляем статус заказа в базе данных
        # Обновляем статус независимо от успеха удаления сообщения
        try:
            order.status = 'processing'
            order.save(update_fields=['status'])
            logger.info(
                f'✅ Заказ {order.order_number} взят в обработку пользователем {user_id} ({user_first_name}). '
                f'Статус обновлен в базе данных.'
            )
        except Exception as e:
            logger.error(f'❌ Ошибка при обновлении статуса заказа {order.order_number}: {e}', exc_info=True)
        
        # Возвращаем успешный ответ Telegram
        return JsonResponse({'ok': True})
        
    except json.JSONDecodeError as e:
        logger.error(f'Invalid JSON in callback: {e}')
        return JsonResponse({'ok': True})  # Отвечаем ok, чтобы Telegram не повторял запрос
    except Exception as e:
        logger.error(f'Ошибка при обработке callback: {e}', exc_info=True)
        return JsonResponse({'ok': True})  # Отвечаем ok, чтобы Telegram не повторял запрос


def custom_404_view(request, exception=None):
    """
    Кастомный обработчик 404 ошибки
    Рендерит красивую страницу 404 в стиле сайта
    """
    from django.shortcuts import render
    from django.template import RequestContext
    from django.http import Http404
    
    try:
        # Пытаемся отрендерить кастомный шаблон 404
        context = {'request': request}
        
        # Пытаемся получить информацию о сайте для контекста
        try:
            from wagtail.models import Site
            site = Site.find_for_request(request)
            if site:
                context['site'] = site
        except Exception:
            pass  # Игнорируем ошибки получения сайта
        
        return render(request, '404.html', context, status=404)
    except Exception as e:
        # Если не удалось отрендерить кастомный шаблон,
        # возвращаем простую страницу 404
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Error rendering 404 template: {e}', exc_info=True)
        
        # Возвращаем простой HTML ответ
        from django.http import HttpResponse
        return HttpResponse(
            '<html><head><title>404 - Page not found</title></head>'
            '<body style="font-family: Arial; text-align: center; padding: 50px;">'
            '<h1>404</h1><p>Page not found</p>'
            '<p><a href="/">Go to homepage</a></p>'
            '</body></html>',
            status=404
        )


def test_404_view(request):
    """
    Тестовый view для просмотра страницы 404 в режиме разработки
    Использование: http://localhost:8000/test-404/
    """
    from django.shortcuts import render
    return render(request, '404.html', status=404)
