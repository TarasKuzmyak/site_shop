from django.urls import path
from . import views
from .views import (
    index, product_list, product_detail, add_review, profile, update_profile, 
    add_address, update_address, set_default_address, wishlist, add_to_wishlist, 
    remove_from_wishlist, cart, update_cart_item, remove_cart_item, checkout, 
    create_order, order_detail, orders, login_view, registration, logout_view, 
    search, change_password, keyboards_view, mouse_view, headsets_view, about_view, 
    contact_view, get_cart, sync_cart, order_success
)
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', index, name='index'),
    path('category/<slug:category_slug>/', product_list, name='product_list_by_category'),
    path('brand/<slug:brand_slug>/', product_list, name='product_list_by_brand'),
    path('category/<slug:category_slug>/brand/<slug:brand_slug>/', product_list, name='product_list_by_category_and_brand'),
    path('product/<slug:slug>/', product_detail, name='product_detail'),
    path('add_review/<int:product_id>/', add_review, name='add_review'),
    path('profile/', profile, name='profile'),
    path('profile/update/', update_profile, name='update_profile'),
    path('profile/add_address/', add_address, name='add_address'),
    path('profile/update_address/<int:address_id>/', update_address, name='update_address'),
    path('profile/set_default_address/<int:address_id>/', set_default_address, name='set_default_address'),
    path('wishlist/', wishlist, name='wishlist'),
    path('add_to_wishlist/<int:product_id>/', add_to_wishlist, name='add_to_wishlist'),
    path('remove_from_wishlist/<int:product_id>/', remove_from_wishlist, name='remove_from_wishlist'),
    path('cart/', cart, name='cart'),
    path('update_cart_item/<int:item_id>/', update_cart_item, name='update_cart_item'),
    path('remove_cart_item/<int:item_id>/', remove_cart_item, name='remove_cart_item'),
    path('checkout/', checkout, name='checkout'),
    path('create_order/', create_order, name='create_order'),
    path('order/success/<int:order_id>/', order_success, name='order_success'),
    path('order/<int:order_id>/', order_detail, name='order_detail'),
    path('orders/', orders, name='orders'),
    path('login/', login_view, name='login'),
    path('register/', registration, name='register'),
    path('logout/', logout_view, name='logout'),
    path('search/', search, name='search'),
    path('change_password/', change_password, name='change_password'),
    path('keyboards/', views.keyboards_view, name='keyboard'),
    path('mice/', mouse_view, name='mouse'),
    path('headsets/', headsets_view, name='headsets'),
    path('about/', about_view, name='about'),
    path('contact/', contact_view, name='contact'),
    path('get_cart/', get_cart, name='get_cart'),
    path('sync_cart/', sync_cart, name='sync_cart'),
    path('register/', views.registration, name='registration'),
    path('create-order/', views.create_order, name='create_order'),
    path('get-cart/', views.get_cart, name='get_cart'),
    path('sync-cart/', views.sync_cart, name='sync_cart'),
    path('products/', views.product_list, name='product_list'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-use/', views.terms_of_use, name='terms_of_use'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)