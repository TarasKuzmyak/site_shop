from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('headsets/', views.headsets, name='headsets'),
    path('keyboard/', views.keyboard, name='keyboard'),
    path('mouse/', views.mouse, name='mouse'),
    path("login/", views.login_view, name="login"),
    path('registration/', views.registration_view, name='registration'),
    path('login/index.html', views.index, name='index'),
    path('login/keyboard/', views.keyboard, name='keyboard'),
    path('login/mouse/', views.mouse, name='mouse'),
    path('login/headsets/', views.headsets, name='headsets'),
    path('registration/index.html', views.index, name='registration_index'),
    path('registration/keyboard/', views.keyboard, name='registration_keyboard'),
    path('registration/mouse/', views.mouse, name='registration_mouse'),
    path('registration/headsets/', views.headsets, name='registration_headsets'),
    path('login/login/keyboard/', views.keyboard, name='keyboard'),
    path('ajazz-ak820-pro/', views.ajazz_ak820_pro_view, name='ajazz_ak820_pro'),
    path('aula_f75/', views.aula_f75_view, name='aula_f75'),
    path('royal_kludge_r75/', views.royal_kludge_r75_veiw, name='royal_kludge_r75'),
    path("aula_f87/", views.aula_f87_view, name="aula_f87"),
    path("ajazz_ak820_pro_moa/", views.ajazz_ak820_pro_moa_view, name='ajazz_ak820_pro_moa'),
    path("ajazz_ak820/", views.ajazz_ak820_view, name="ajazz_ak820"),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('buy/<int:product_id>/', views.buy_product_view, name='buy_product'),
    path('/login/ajazz_ak820/', views.product_detail, name='product_detail'),


    


]
