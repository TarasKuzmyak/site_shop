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
from django.contrib.auth import logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse








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

        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
        except User.DoesNotExist:
            return JsonResponse({"success": False, "errors": {"email": "Користувача з таким email не знайдено!"}})
        
        if user is not None:
            login(request, user)
            return JsonResponse({"success": True, "redirect_url": f"/profile/{user.username}/"})  # 🔹 Перенаправлення
        else:
            return JsonResponse({"success": False, "errors": {"password": "Неправильний пароль!"}})
    
    return JsonResponse({"success": False, "errors": {"general": "Невірний запит!"}})


@csrf_exempt
def registration(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        errors = {}

        if not first_name:
            errors["first_name"] = "Поле 'Ім'я' не може бути порожнім!"
        if not last_name:
            errors["last_name"] = "Поле 'Прізвище' не може бути порожнім!"
        if not email:
            errors["email"] = "Введіть email!"
        elif User.objects.filter(email=email).exists():
            errors["email"] = "Користувач з таким email вже існує!"

        if len(password) < 6:
            errors["password"] = "Пароль має бути не менше 6 символів!"
        if password != confirm_password:
            errors["confirm_password"] = "Паролі не співпадають!"

        if errors:
            return JsonResponse({"success": False, "errors": errors})

        user = User.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=email,
            password=make_password(password),
        )
        return JsonResponse({"success": True, "redirect_url": "/profile/" + user.username + "/"})

    return JsonResponse({"success": False, "errors": {"general": "Невірний запит!"}})




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


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Product, CartItem
from django.contrib.sessions.models import Session


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Product, CartItem

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Product, CartItem

# 🔹 Тимчасово вимкни CSRF, якщо проблема в токені
from django.http import JsonResponse
import json

def add_to_cart(request):
    if request.method == "POST":
        try:
            print("✅ Запит отримано:", request.body)  # 🔹 Додаємо лог
            data = json.loads(request.body)
            product_id = data.get("id")

            if not product_id:
                return JsonResponse({"success": False, "error": "ID товару не передано!"}, status=400)

            if request.user.is_authenticated:
                product = Product.objects.get(id=product_id)
                Cart.objects.create(user=request.user, product=product)
                return JsonResponse({"success": True, "message": "Товар додано у кошик!"})

            return JsonResponse({"success": True, "message": "Товар додано у локальний кошик!"})

        except Product.DoesNotExist:
            return JsonResponse({"success": False, "error": "Товар не знайдено!"}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Помилка JSON!"}, status=400)

    return JsonResponse({"success": False, "error": "Метод не підтримується!"}, status=405)






def cart_view(request):
    return render(request, "cart.html")



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

def logout_view(request):
    logout(request)  # 🔹 Завершуємо сесію користувача
    return redirect("index")  # 🔹 Перенаправляємо на головну сторінку

from django.http import JsonResponse
from .models import CartItem

def cart_data(request):
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
        data = {
            "cart_items": [
                {
                    "id": item.id,
                    "name": item.product.name,
                    "image": item.product.image.url,
                    "quantity": item.quantity,
                    "total_price": item.total_price(),
                }
                for item in cart_items
            ]
        }
    else:
        data = {"cart_items": []}
    
    return JsonResponse(data)


def check_auth_status(request):
    return JsonResponse({"is_authenticated": request.user.is_authenticated})

