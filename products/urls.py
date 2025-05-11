from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.index, name='index'),  # Головна сторінка
    path('keyboard/', views.keyboard, name='keyboard'),
    path('mouse/', views.mouse, name='mouse'),
    path('headsets/', views.headsets, name='headsets'),
    path('login/', views.login_view, name='login'),
    path('registration/', views.registration, name='registration'),
    path('/login/mouse/headsets.html', views.headsets, name='headsets'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    
    path('profile/', views.profile, name='profile'),

    # Маршрути для продуктів
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('ajazz-ak820/', views.ajazz_ak820_view, name='ajazz_ak820'),
    path('ajazz-ak820-pro/', views.ajazz_ak820_pro_view, name='ajazz_ak820_pro'),
    path('ajazz-ak820-pro-moa/', views.ajazz_ak820_pro_moa_view, name='ajazz_ak820_pro_moa'),
    path('aula_f75/', views.aula_f75_view, name='aula_f75'),
    path('royal-kludge-r75/', views.royal_kludge_r75_view, name='royal_kludge_r75'),
    path('aula_f87/', views.aula_f87_view, name='aula_f87'),

    # Кошик та покупка
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('buy/<int:product_id>/', views.buy_product_view, name='buy_product'),
    
    path("password-reset/", auth_views.PasswordResetView.as_view(), name="password_reset"),
    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("password-reset-confirm/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("password-reset-complete/", auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),
]
