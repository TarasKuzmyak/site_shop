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

from .models import (
    Product, Category, Brand, Review, 
    UserProfile, Address, Wishlist, 
    Order, OrderItem, CartItem, User
)
from .forms import RegistrationForm, ReviewForm

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
    
    # Фільтрація
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Сортування
    sort_by = request.GET.get('sort_by', '-created_at')
    if sort_by in ['price', '-price', 'name', '-name', '-created_at']:
        products = products.order_by(sort_by)
    
    # Пагінація
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'brand': brand,
        'products': page_obj,
        'sort_by': sort_by,
        'min_price': min_price,
        'max_price': max_price,
    }
    return render(request, 'products/product_list.html', context) 

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
    
    context = {
        'user': user,
        'profile': profile,
        'orders': orders,
        'wishlist': wishlist,
    }
    return render(request, 'products/profile.html', context)

@login_required
def update_profile(request):
    if request.method == 'POST':
        user = request.user
        profile = user.userprofile
        
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.save()
        
        profile.phone = request.POST.get('phone', profile.phone)
        profile.birth_date = request.POST.get('birth_date', profile.birth_date)
        profile.gender = request.POST.get('gender', profile.gender)
        
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
        
        profile.save()
        messages.success(request, 'Профіль успішно оновлено!')
        return redirect('profile')
    
    return redirect('profile')

@login_required
def add_address(request):
    if request.method == 'POST':
        address = Address(
            user=request.user,
            name=request.POST.get('name'),
            recipient=request.POST.get('recipient'),
            phone=request.POST.get('phone'),
            city=request.POST.get('city'),
            address=request.POST.get('address'),
            postal_code=request.POST.get('postal_code'),
            is_default=request.POST.get('is_default', False) == 'on'
        )
        address.save()
        messages.success(request, 'Адресу успішно додано!')
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
        return sum(item['quantity'] for item in cart.values())

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
    addresses = request.user.addresses.all()
    
    if request.method == 'POST':
        shipping_address_id = request.POST.get('shipping_address')
        billing_address_id = request.POST.get('billing_address', shipping_address_id)
        payment_method = request.POST.get('payment_method')
        note = request.POST.get('note', '')
        
        try:
            shipping_address = Address.objects.get(id=shipping_address_id, user=request.user)
            billing_address = Address.objects.get(id=billing_address_id, user=request.user)
            
            order = Order.objects.create(
                user=request.user,
                shipping_address=shipping_address,
                billing_address=billing_address,
                note=note,
                total_price=total_price
            )
            
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )
            
            # Очистити кошик
            cart_items.delete()
            
            messages.success(request, 'Замовлення успішно оформлено!')
            return redirect('order_detail', order_id=order.id)
        
        except Exception as e:
            messages.error(request, f'Помилка при оформленні замовлення: {str(e)}')
    
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'addresses': addresses,
    }
    return render(request, 'products/checkout.html', context)

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'products/order_detail.html', {'order': order})

@login_required
def orders(request):
    orders = request.user.orders.all().order_by('-created_at')
    return render(request, 'orders.html', {'orders': orders}) 

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'success': True, 'redirect_url': '/'})
        else:
            return JsonResponse({'success': False, 'error': 'Невірний email або пароль'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def registration(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            
            if User.objects.filter(email=email).exists():
                return JsonResponse({'success': False, 'error': 'Користувач з таким email вже існує'})
            
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                username=email.split('@')[0]
            )
            
            login(request, user)
            return JsonResponse({'success': True, 'redirect_url': '/'})
        
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

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

from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash


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
            messages.error(request, 'Будь ласка, виправте помилки нижче.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'products/change_password.html', {'form': form})

def keyboard(request):
    keyboard = Product.objects.filter(category="keyboard")
    return render(request, 'products/keyboard.html', {'keyboard': keyboard})  # ОНОВЛЕНО

def mouse(request):
    mice = Product.objects.filter(category="mouse")
    return render(request, 'products/mouse.html', {'mice': mice})

def headsets(request):
    headsets = Product.objects.filter(category='headsets')  # Припустимо, що така модель є
    return render(request, 'products/headsets.html', {'headsets': headsets})


def about_view(request):
    return render(request, 'products/about.html')

def contact_view(request):
    return render(request, 'products/contact.html')