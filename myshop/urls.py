from django.contrib import admin
from django.urls import path, include
from products import views
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views



urlpatterns = [
    # 🔹 Адмін-панель
    path('admin/', admin.site.urls),

    # 🔹 Автентифікація
    path("login/", views.login_view, name="login"),
    path('registration/', views.registration, name='registration'),
    path('logout/', LogoutView.as_view(next_page='index'), name='logout'),

    # 🔹 Профіль користувача
    path("profile/", views.profile, name="profile"),




    path('orders/', views.orders, name='orders'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('change-password/', views.change_password, name='change_password'),

    # 🔹 Категорії товарів
    path('mouse/', views.mouse, name='mouse'),
    path('keyboard/', views.keyboard, name='keyboard'),
    path('headsets/', views.headsets, name='headsets'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),

    # 🔹 Конкретні моделі клавіатур
    path('ajazz-ak820/', views.ajazz_ak820_view, name='ajazz_ak820'),
    path('ajazz-ak820-pro/', views.ajazz_ak820_pro_view, name='ajazz_ak820_pro'),
    path('ajazz-ak820-pro-moa/', views.ajazz_ak820_pro_moa_view, name='ajazz_ak820_pro_moa'),
    path('aula_f75/', views.aula_f75_view, name='aula_f75'),
    path('royal-kludge-r75/', views.royal_kludge_r75_view, name='royal_kludge_r75'),
    path('aula_f87/', views.aula_f87_view, name='aula_f87'),

    # 🔹 Кошик та покупки
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('buy/<int:product_id>/', views.buy_product_view, name='buy_product'),

    # 🔹 Підключення додаткових маршрутів
    path('', include('products.urls')),  # Важливо: має бути останнім
]