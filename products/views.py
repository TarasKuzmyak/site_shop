from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from django.conf import settings
import json
from datetime import datetime
import requests
from urllib.parse import unquote
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

from .models import (
    Product, Category, Brand, Review, 
    UserProfile, Address, Wishlist, 
    Order, OrderItem, CartItem, User
)
from .forms import RegistrationForm, ReviewForm, PasswordChangeForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

def index(request):
    featured_products = Product.objects.filter(is_featured=True)[:8]
    new_products = Product.objects.filter(is_new=True)[:8]
    popular_products = Product.objects.annotate(
        review_count=Count('reviews')
    ).order_by('-review_count')[:8]
    
    categories = Category.objects.all()[:6]
    
    context = {
        'featured_products': featured_products,
        'new_products': new_products,
        'popular_products': popular_products,
        'categories': categories,
    }
    return render(request, 'products/index.html', context)

def product_list(request, category_slug=None, brand_slug=None):
    products = Product.objects.filter(is_available=True)
    category = None
    brand = None
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    if brand_slug:
        brand = get_object_or_404(Brand, slug=brand_slug)
        products = products.filter(brand=brand)
    
    # Сортування
    sort_by = request.GET.get('sort_by', '-created_at')
    if sort_by in ['price', '-price', 'name', '-name', '-created_at']:
        products = products.order_by(sort_by)
    
    # Пагінація
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    return render(request, 'products/product_list.html', {
        'category': category,
        'brand': brand,
        'products': products,
        'sort_by': sort_by
    })

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.filter(
        category=product.category
    ).exclude(id=product.id)[:4]
    
    # Отримання відгуків
    reviews = product.reviews.all()
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    # Форма для відгуку
    review_form = None
    if request.user.is_authenticated:
        has_reviewed = reviews.filter(user=request.user).exists()
        if not has_reviewed:
            review_form = ReviewForm()
    
    context = {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'average_rating': round(average_rating, 1),
        'review_form': review_form,
    }
    return render(request, 'products/product_detail.html', context)

@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, 'Ваш відгук успішно додано!')
            return redirect('product_detail', slug=product.slug)
    
    messages.error(request, 'Не вдалося додати відгук')
    return redirect('product_detail', slug=product.slug)

@login_required
def profile(request):
    user = request.user
    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user)
    
    orders = user.orders.all()[:5]
    wishlist = user.wishlist.all()[:6]
    addresses = user.addresses.all()
    
    context = {
        'user': user,
        'profile': profile,
        'orders': orders,
        'wishlist': wishlist,
        'addresses': addresses
    }
    return render(request, 'products/profile.html', context)

@login_required
def update_profile(request):
    if request.method == 'POST':
        user = request.user
        
        # Оновлюємо дані користувача
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        
        # Перевіряємо email на унікальність
        new_email = request.POST.get('email')
        if new_email and new_email != user.email:
            if User.objects.filter(email=new_email).exclude(id=user.id).exists():
                messages.error(request, 'Цей email вже використовується іншим користувачем')
                return redirect('profile')
            user.email = new_email
        
        user.save()
        
        # Оновлюємо профіль
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.phone = request.POST.get('phone', profile.phone)
        
        birth_date = request.POST.get('birth_date')
        if birth_date:
            try:
                # Перетворюємо рядок у дату
                profile.birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, 'Невірний формат дати')
                return redirect('profile')
        
        profile.gender = request.POST.get('gender', profile.gender)
        profile.save()
        
        messages.success(request, 'Профіль успішно оновлено!')
        return redirect('profile')
    
    return redirect('profile')

@login_required
def add_address(request):
    if request.method == 'POST':
        # Обробка адреси за замовчуванням
        is_default = request.POST.get('is_default') == 'on'
        if is_default:
            # Знімаємо позначку з інших адрес
            Address.objects.filter(user=request.user).update(is_default=False)
            
        address = Address(
            user=request.user,
            name=request.POST.get('name'),
            recipient=request.POST.get('recipient'),
            phone=request.POST.get('phone'),
            city=request.POST.get('city'),
            address=request.POST.get('address'),
            postal_code=request.POST.get('postal_code'),
            is_default=is_default
        )
        address.save()
        messages.success(request, 'Адресу успішно додано!')
    return redirect('profile')

@login_required
def update_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    if request.method == 'POST':
        # Обробка адреси за замовчуванням
        is_default = request.POST.get('is_default') == 'on'
        if is_default:
            # Знімаємо позначку з інших адрес
            Address.objects.filter(user=request.user).update(is_default=False)
        
        address.name = request.POST.get('name', address.name)
        address.recipient = request.POST.get('recipient', address.recipient)
        address.phone = request.POST.get('phone', address.phone)
        address.city = request.POST.get('city', address.city)
        address.address = request.POST.get('address', address.address)
        address.postal_code = request.POST.get('postal_code', address.postal_code)
        address.is_default = is_default
        address.save()
        
        messages.success(request, 'Адресу успішно оновлено!')
        return redirect('profile')
    
    return redirect('profile')

@login_required
def set_default_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    # Знімаємо позначку з інших адрес
    Address.objects.filter(user=request.user).update(is_default=False)
    
    # Встановлюємо поточну адресу як основну
    address.is_default = True
    address.save()
    
    messages.success(request, 'Основну адресу змінено')
    return redirect('profile')

@login_required
def wishlist(request):
    wishlist_items = request.user.wishlist.all()
    return render(request, 'products/wishlist.html', {'wishlist_items': wishlist_items}) 

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.get_or_create(user=request.user, product=product)
    return JsonResponse({'success': True})

@login_required
def remove_from_wishlist(request, product_id):
    Wishlist.objects.filter(user=request.user, product_id=product_id).delete()
    return JsonResponse({'success': True})

@csrf_exempt
def add_to_cart(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            quantity = int(data.get('quantity', 1))
            
            product = get_object_or_404(Product, id=product_id)
            
            if request.user.is_authenticated:
                cart_item, created = CartItem.objects.get_or_create(
                    user=request.user,
                    product=product,
                    defaults={'quantity': quantity}
                )
                if not created:
                    cart_item.quantity += quantity
                    cart_item.save()
            else:
                # Обробка для неавторизованих користувачів через сесію
                cart = request.session.get('cart', {})
                cart_item = cart.get(str(product_id), {'quantity': 0})
                cart_item['quantity'] += quantity
                cart[str(product_id)] = cart_item
                request.session['cart'] = cart
                request.session.modified = True
            
            return JsonResponse({
                'success': True,
                'cart_count': get_cart_count(request)
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def get_cart_count(request):
    if request.user.is_authenticated:
        return CartItem.objects.filter(user=request.user).count()
    else:
        cart = request.session.get('cart', {})
        return sum(item['quantity'] for item in cart.values() if isinstance(item, dict))

@login_required
def cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'products/cart.html', context)

@login_required
def update_cart_item(request, item_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
        
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()
        
        return redirect('cart')

@login_required
def remove_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    cart_item.delete()
    return redirect('cart')

@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    if not cart_items.exists():
        return redirect('cart')
    
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    
    if request.method == 'POST':
        # Отримуємо дані форми
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        nova_poshta_city = request.POST.get('nova_poshta_city')
        nova_poshta_city_ref = request.POST.get('nova_poshta_city_ref')
        nova_poshta_department = request.POST.get('nova_poshta_department')
        nova_poshta_department_name = request.POST.get('nova_poshta_department_name')
        
        try:
            # Створюємо замовлення
            order = Order.objects.create(
                user=request.user,
                total_price=total_price,
                payment_method='cash_on_delivery',
                nova_poshta_city=nova_poshta_city,
                nova_poshta_city_ref=nova_poshta_city_ref,
                nova_poshta_department=nova_poshta_department,
                nova_poshta_department_name=nova_poshta_department_name,
                customer_name=full_name,
                customer_phone=phone,
                customer_email=email,
                status='pending'
            )
            
            # Додаємо товари до замовлення
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )
            
            # Надсилаємо email про замовлення
            subject = f"Ваше замовлення #{order.order_number} прийнято"
            message = f"Дякуємо за замовлення, {full_name}!\n\n" \
                      f"Номер замовлення: {order.order_number}\n" \
                      f"Сума: {total_price} грн\n" \
                      f"Статус: В обробці\n\n" \
                      f"Очікуйте дзвінка менеджера для підтвердження."
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            
            # Очищаємо кошик
            cart_items.delete()
            
            # Перенаправляємо на сторінку успіху
            return redirect(reverse('order_success', kwargs={'order_id': order.id}))
        
        except Exception as e:
            messages.error(request, f'Помилка при оформленні замовлення: {str(e)}')
            return redirect('checkout')
    
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'products/checkout.html', context)

@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'products/order_success.html', {'order': order})

@login_required
@require_POST
@csrf_exempt
def create_order(request):
    """Обробка AJAX-запиту на створення замовлення"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Користувач не авторизований'})
    
    cart_items = CartItem.objects.filter(user=request.user)
    if not cart_items.exists():
        return JsonResponse({'success': False, 'error': 'Кошик порожній'})
    
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    
    try:
        # Отримуємо дані користувача
        customer_name = f"{request.user.first_name} {request.user.last_name}"
        customer_phone = request.user.userprofile.phone if hasattr(request.user, 'userprofile') else ""
        customer_email = request.user.email

        # Створення замовлення
        order = Order.objects.create(
            user=request.user,
            total_price=total_price,
            payment_method='cash_on_delivery',
            status='pending',
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_email=customer_email
        )
        
        # Додавання товарів до замовлення
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
        
        # Очищення кошика
        cart_items.delete()
        
        return JsonResponse({
            'success': True,
            'order_id': order.id,
            'redirect_url': reverse('orders')  # Додаємо URL для перенаправлення
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Помилка при створенні замовлення: {str(e)}'
        })

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'products/order_detail.html', {'order': order})

@login_required
def orders(request):
    orders = request.user.orders.all().order_by('-created_at')
    return render(request, 'products/orders.html', {'orders': orders})

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        next_url = request.POST.get('next', '/')  # Отримуємо параметр next
        
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'success': True, 'redirect_url': next_url})
        else:
            return JsonResponse({'success': False, 'error': 'Невірний email або пароль'})
    
    # Обробляємо GET-запити для перенаправлення
    if request.method == 'GET':
        next_url = request.GET.get('next', '/')
        return JsonResponse({
            'success': False, 
            'error': 'Необхідна авторизація',
            'redirect_url': f'/login/?next={next_url}'
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def registration(request):
    if request.method == 'POST':
        try:
            data = request.POST
            email = data.get('email')
            password = data.get('password')
            confirm_password = data.get('confirm_password')
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            
            # Перевірка наявності всіх полів
            if not all([email, password, confirm_password, first_name, last_name]):
                return JsonResponse({'success': False, 'error': 'Усі поля обовʼязкові'})
                
            # Перевірка довжини пароля
            if len(password) < 8:
                return JsonResponse({'success': False, 'error': 'Пароль має містити принаймні 8 символів'})
                
            # Перевірка співпадіння паролів
            if password != confirm_password:
                return JsonResponse({'success': False, 'error': 'Паролі не співпадають'})
                
            # Перевірка унікальності email
            User = get_user_model()
            if User.objects.filter(email=email).exists():
                return JsonResponse({'success': False, 'error': 'Email вже використовується'})
                
            # Створення користувача
            user = User.objects.create_user(
                email=email,
                password=password,
                username=email.split('@')[0],
                first_name=first_name,
                last_name=last_name
            )
            
            # Автоматичний вхід користувача після реєстрації
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({
                    'success': True, 
                    'redirect_url': reverse('profile')  # Використовуємо reverse
                })
            else:
                return JsonResponse({'success': False, 'error': 'Помилка автентифікації'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Невірний метод запиту'})

def logout_view(request):
    logout(request)
    return redirect('index')

def search(request):
    query = request.GET.get('q', '')
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(category__name__icontains=query) |
            Q(brand__name__icontains=query)
        ).distinct()
    else:
        products = Product.objects.none()
    
    context = {
        'query': query,
        'products': products,
    }
    return render(request, 'products/search.html', context) 

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Важливо, щоб користувач не вийшов з системи
            messages.success(request, 'Ваш пароль успішно змінено!')
            return redirect('profile')
        else:
            messages.error(request, 'Будь ласка, виправте помилки')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'products/change_password.html', {'form': form})

def keyboards_view(request):
    category = get_object_or_404(Category, slug='keyboards')
    products = Product.objects.filter(category=category, is_available=True)
    return render(request, 'products/keyboard.html', {
        'products': products,
        'category': category
    })

def mouse_view(request):
    category = get_object_or_404(Category, slug='mice')
    products = Product.objects.filter(
        category=category, 
        is_available=True
    ).select_related('category').prefetch_related('images')
    
    # Сортування
    sort_by = request.GET.get('sort_by', '-created_at')
    if sort_by in ['price', '-price', 'name', '-name', '-created_at']:
        products = products.order_by(sort_by)
    
    # Пагінація
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    context = {
        'products': products,
        'category': category,
        'sort_by': sort_by
    }
    return render(request, 'products/mouse.html', context)

def headsets_view(request):
    category = get_object_or_404(Category, slug='headsets')
    products = Product.objects.filter(
        category=category, 
        is_available=True
    ).annotate(
        reviews_count=Count('reviews')
    ).select_related('category').prefetch_related('images')
    
    # Сортування
    sort_by = request.GET.get('sort_by', '-created_at')
    if sort_by in ['price', '-price', 'name', '-name', '-created_at']:
        products = products.order_by(sort_by)
    
    # Пагінація
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    context = {
        'products': products,
        'category': category,
        'sort_by': sort_by
    }
    return render(request, 'products/headsets.html', context)

def about_view(request):
    return render(request, 'products/about.html')

def contact_view(request):
    return render(request, 'products/contact.html')

@csrf_exempt
def get_cart(request):
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user).select_related('product')
        cart_data = [
            {
                'id': item.product.id,
                'name': item.product.name,
                'price': float(item.product.price),
                'quantity': item.quantity,
                'image': item.product.main_image.url if item.product.main_image else ''
            }
            for item in cart_items
        ]
        return JsonResponse(cart_data, safe=False)
    
    # Обробка для неавторизованих користувачів
    cart = request.session.get('cart', {})
    cart_data = []
    for product_id, item in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            cart_data.append({
                'id': product.id,
                'name': product.name,
                'price': float(product.price),
                'quantity': item['quantity'],
                'image': product.main_image.url if product.main_image else ''
            })
        except Product.DoesNotExist:
            continue
    
    return JsonResponse(cart_data, safe=False)

@csrf_exempt
def sync_cart(request):
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            cart_data = json.loads(request.body)
            
            # Очистити існуючий кошик користувача
            CartItem.objects.filter(user=request.user).delete()
            
            # Додати товари з localStorage
            for item in cart_data:
                product = get_object_or_404(Product, id=item['id'])
                CartItem.objects.create(
                    user=request.user,
                    product=product,
                    quantity=item['quantity']
                )
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})


def privacy_policy(request):
    return render(request, 'products/privacy_policy.html')

def terms_of_use(request):
    return render(request, 'products/terms_of_use.html')