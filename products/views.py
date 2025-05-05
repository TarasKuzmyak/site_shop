from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Cart, Product



def index(request):
    return render(request, 'products/index.html')

def headsets(request):
    return render(request, 'products/headsets.html')

def keyboard(request):
    products = Product.objects.filter(category="keyboard")  # Фільтруємо клавіатури
    return render(request, 'products/keyboard.html', {'products': products})

def mouse(request):
    return render(request, 'products/mouse.html')

def login_view(request):
    return render(request, 'products/login.html')

def registration_view(request):
    if request.method == 'POST':
        # обробка форми реєстрації
        pass
    return render(request, 'products/login.html')

def ajazz_ak820_pro_view(request):
    return render(request, 'products/main_keyboard/AJAZZ AK820 Pro MOA.html')

def aula_f75_view(request):
    return render(request, 'products/main_keyboard/Aulaf75.html')

def royal_kludge_r75_veiw(request):
    return render(request, 'products/main_keyboard/Royal Kludge R75.html')

def aula_f87_view(request):
    return render(request, 'products/main_keyboard/AULA F87.html')

def ajazz_ak820_pro_moa_view(request):
    return render(request, 'products/main_keyboard/AJAZZ AK820 Pro MOA.html')

def ajazz_ak820_view(request):
    product = get_object_or_404(Product, name="AJAZZ AK820")  
    return render(request, 'products/main_product/main_keyboard/AJAZZ  AK 820.html', {'product': product})


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart')

@login_required
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.total_price() for item in cart_items)
    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(Cart, id=item_id, user=request.user)
    cart_item.delete()
    return redirect('cart')


def buy_product_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'products/buy.html', {'product': product})

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'products/main_product/main_keyboard/AJAZZ  AK 820.html', {'product': product})
