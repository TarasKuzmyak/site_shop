from django.contrib import admin
from .models import (
    Product, Category, Brand, ProductSpecification, ProductImage,
    Review, UserProfile, Address, Wishlist, Order, OrderItem, User, CartItem
)

# Inlines для покращеного відображення пов'язаних об'єктів
class ProductImageInline(admin.TabularInline):
    model = Product.images.through
    extra = 1
    verbose_name = "Зображення"
    verbose_name_plural = "Зображення продукту"

class ProductSpecificationInline(admin.TabularInline):
    model = Product.specifications.through
    extra = 1
    verbose_name = "Специфікація"
    verbose_name_plural = "Специфікації продукту"

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('product', 'quantity', 'price', 'total_price')
    can_delete = False
    extra = 0

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "description", "image")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "description")

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "description", "logo")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "description")

@admin.register(ProductSpecification)
class ProductSpecificationAdmin(admin.ModelAdmin):
    list_display = ("name", "value")
    search_fields = ("name", "value")
    list_filter = ("name",)

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("id", "image", "is_main")
    list_filter = ("is_main",)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name", "price", "stock", "category", "brand", "is_available",
        "is_new", "is_featured", "discount", "created_at"
    )
    list_filter = ("category", "brand", "is_available", "is_new", "is_featured", "created_at")
    search_fields = ("name", "short_description", "full_description", "sku")
    prepopulated_fields = {"slug": ("name",)}
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    fieldsets = (
        (None, {
            'fields': (
                'name', 'slug', 'category', 'brand', 'sku', 'price', 'old_price', 'discount',
                'stock', 'is_available', 'is_new', 'is_featured'
            )
        }),
        ('Опис', {
            'fields': ('short_description', 'full_description'),
            'classes': ('collapse',)
        }),
        ('Додаткові деталі', {
            'fields': ('warranty', 'weight'),
            'classes': ('collapse',)
        }),
    )
    inlines = [ProductImageInline, ProductSpecificationInline]

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating", "created_at", "updated_at")
    list_filter = ("rating", "created_at")
    search_fields = ("product__name", "user__username", "text")
    raw_id_fields = ('product', 'user')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "birth_date", "gender", "avatar")
    search_fields = ("user__username", "phone")
    raw_id_fields = ('user',)

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("user", "name", "city", "address", "postal_code", "is_default")
    list_filter = ("city", "is_default")
    search_fields = ("user__username", "city", "address", "postal_code")
    raw_id_fields = ('user',)

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "added_at")
    list_filter = ("added_at",)
    search_fields = ("user__username", "product__name")
    raw_id_fields = ('user', 'product')

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_price', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__email', 'id']
    raw_id_fields = ['user']
    inlines = [OrderItemInline]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity", "price", "total_price")
    search_fields = ("order__order_number", "product__name")
    list_filter = ("order__status",)
    raw_id_fields = ('order', 'product')

@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("email", "username", "is_staff", "is_active", "date_joined")
    list_filter = ("is_staff", "is_active", "date_joined")
    search_fields = ("email", "username")

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "quantity", "added_at", "total_price")
    list_filter = ("added_at",)
    search_fields = ("user__username", "product__name")
    raw_id_fields = ('user', 'product')

# Видалено всі дублюючі реєстрації в кінці файлу
# Залишаємо тільки реєстрацію для Order, так як інші моделі вже зареєстровані через @admin.register
admin.site.register(Order, OrderAdmin)