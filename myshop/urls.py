from django.contrib import admin
from django.urls import path, include # Важливо: додайте 'include'
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # Усі URL-шляхи з додатку 'products' тепер будуть доступні
    # без префікса, оскільки ми включаємо їх з порожнім шляхом ('')
    path('', include('products.urls')), 
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)