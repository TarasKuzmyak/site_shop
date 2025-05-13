from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Cart, Product
from django.contrib.auth import login, authenticate
from .forms import RegistrationForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .models import Order
from django.http import HttpResponse
from django.contrib.auth import get_user_model






User = get_user_model()





def index(request):
    return render(request, 'products/index.html')


def headsets(request):
    headsets = Product.objects.filter(category='headsets')  # Припустимо, що така модель є
    return render(request, 'products/headsets.html', {'headsets': headsets})


def keyboard(request):
    keyboards = Product.objects.filter(category="keyboard")
    return render(request, 'products/keyboard.html', {'keyboards': keyboards})  # ОНОВЛЕНО




def mouse(request):
    mice = Product.objects.filter(category="mouse")
    return render(request, 'products/mouse.html', {'mice': mice})
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        user = None  # 🔹 Додаємо початкове значення, щоб уникнути UnboundLocalError

        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
        except User.DoesNotExist:
            return JsonResponse({"success": False, "errors": {"email": "Користувача з таким email не знайдено!"}})

        if user is not None:
            login(request, user)
            return JsonResponse({"success": True, "redirect_url": f"/profile/{user.username}/"})
        else:
            return JsonResponse({"success": False, "errors": {"password": "Неправильний пароль!"}})

    return JsonResponse({"success": False, "errors": {"general": "Невірний запит!"}})




def registration(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data["email"].strip()  # 🔹 Забираємо зайві пробіли/символи
            user.set_password(form.cleaned_data["password"])
            user.save()
            login(request, user)  
            return redirect("profile", username=user.username)
    else:
        form = RegistrationForm()

    return render(request, "products/registration.html", {"form": form})




def profile(request, username):
    user = get_object_or_404(User, username=username)  # 🔹 Надійний спосіб отримати користувача
    return render(request, "products/profile.html", {"user": user})




    

@login_required
def orders(request):
    # Якщо у тебе є модель Order, отримай замовлення користувача
    user_orders = request.user.order_set.all() if hasattr(request.user, "order_set") else []
    
    return render(request, "orders.html", {"orders": user_orders})

@login_required
def wishlist(request):
    # Отримати список товарів із списку бажаного користувача (якщо є відповідна модель)
    user_wishlist = request.user.wishlist.all() if hasattr(request.user, "wishlist") else []
    
    return render(request, "wishlist.html", {"wishlist": user_wishlist})    

@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Щоб не розлогінити користувача після зміни пароля
            return redirect("profile")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, "change_password.html", {"form": form})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)  # Переконуємося, що замовлення належить користувачу
    return render(request, "order_detail.html", {"order": order})


def ajazz_ak820_pro_view(request):
    product = get_object_or_404(Product, name="AJAZZ AK820 Pro")  # Отримуємо продукт
    return render(request, 'products/main_product/main_keyboard/Ajazz820pro.html', {'product': product})

def aula_f75_view(request):
    product = get_object_or_404(Product, name="AULA F75")  # Отримуємо продукт
    return render(request, 'products/main_product/main_keyboard/Aulaf75.html', {'product': product})


def royal_kludge_r75_view(request):
    product = get_object_or_404(Product, name="Royal Kludge R75")  # Отримуємо продукт
    return render(request, 'products/main_product/main_keyboard/Royal Kludge R75.html', {'product': product})


def aula_f87_view(request):
    product = Product.objects.filter(name="AULA F87").first()  # Беремо перший запис
    if not product:
        return render(request, 'products/main_product/main_keyboard/AULA F87.html', {'error': "Продукт не знайдено"})
    return render(request, 'products/main_product/main_keyboard/AULA F87.html', {'product': product})


def ajazz_ak820_pro_moa_view(request):
    product = get_object_or_404(Product, name="AJAZZ AK820 Pro MOA")  # Забезпечуємо, що продукт існує
    return render(request, 'products/main_product/main_keyboard/AJAZZ_AK820_Pro_MOA.html', {'product': product})
 



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

