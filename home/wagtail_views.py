"""
Views для обработки bulk actions в Wagtail админ-панели.

Этот модуль содержит представления для массовых операций с заказами
в админ-панели Wagtail (удаление выбранных заказов, удаление всех заказов).
"""
from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Order


@require_POST
@login_required
@user_passes_test(lambda u: u.is_staff)
def delete_selected_orders(request):
    """
    Удаление выбранных заказов.
    
    Принимает список ID заказов из POST запроса и удаляет их.
    Использует транзакцию для обеспечения атомарности операции.
    
    Args:
        request: HTTP запрос с POST данными, содержащими список 'selected' с ID заказов
        
    Returns:
        HttpResponseRedirect: Перенаправление на страницу списка заказов
    """
    try:
        selected_ids = request.POST.getlist('selected')
        
        if not selected_ids:
            messages.warning(request, 'Не выбрано ни одного заказа для удаления')
            return redirect('/admin/order/')
        
        # Преобразуем ID в целые числа и фильтруем пустые значения
        order_ids = [int(oid) for oid in selected_ids if oid]
        orders = Order.objects.filter(id__in=order_ids)
        count = orders.count()
        
        if count > 0:
            with transaction.atomic():
                orders.delete()
            messages.success(request, f'Успешно удалено {count} заказ(ов)')
        else:
            messages.warning(request, 'Выбранные заказы не найдены')
    except (ValueError, TypeError) as e:
        messages.error(request, f'Ошибка при обработке ID заказов: {e}')
    except Exception as e:
        messages.error(request, f'Ошибка при удалении: {e}')
    
    # Перенаправляем обратно на страницу списка заказов
    return redirect('/admin/order/')


@require_POST
@login_required
@user_passes_test(lambda u: u.is_staff)
def delete_all_orders(request):
    """
    Удаление всех заказов из базы данных.
    
    ВНИМАНИЕ: Это опасная операция, которая удаляет все заказы без возможности восстановления.
    Использует транзакцию для обеспечения атомарности операции.
    
    Args:
        request: HTTP запрос
        
    Returns:
        HttpResponseRedirect: Перенаправление на страницу списка заказов
    """
    try:
        count = Order.objects.count()
        if count > 0:
            with transaction.atomic():
                Order.objects.all().delete()
            messages.success(request, f'Успешно удалено {count} заказ(ов)')
        else:
            messages.info(request, 'Нет заказов для удаления')
    except Exception as e:
        messages.error(request, f'Ошибка при удалении: {e}')
    
    # Перенаправляем обратно на страницу списка заказов
    return redirect('/admin/order/')
