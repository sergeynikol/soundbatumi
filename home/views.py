from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _, gettext
from django.db import transaction
from decimal import Decimal, InvalidOperation
import json
import random
from datetime import datetime
from .models import Order, OrderItem, UserProfile


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
        delivery_address = data.get('delivery_address', '').strip()
        customer_name = data.get('customer_name', '').strip()
        customer_phone = data.get('customer_phone', '').strip()
        customer_email = data.get('customer_email', '').strip()
        customer_comment = data.get('customer_comment', '').strip()
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
                status='pending',
                user=request.user if request.user.is_authenticated else None
            )
            
            # Создаем позиции заказа
            total_amount = Decimal('0.00')
            for item in cart_items:
                try:
                    unit_price = Decimal(str(item.get('price', 0)))
                    quantity = int(item.get('quantity', 1))
                    
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

