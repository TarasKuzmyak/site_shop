from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings
from django.utils.text import slugify
import datetime
from django.utils import timezone
import random

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Brand(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='brand_logos/', blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class ProductSpecification(models.Model):
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=255)
    
    def __str__(self):
        return f"{self.name}: {self.value}"

class ProductImage(models.Model):
    image = models.ImageField(upload_to='product_images/')
    is_main = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Image {self.id}"

class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    short_description = models.TextField(blank=True)
    full_description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=50, unique=True)
    stock = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    is_new = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    warranty = models.PositiveIntegerField(default=12)  # місяців
    weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)  # в грамах
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image_path = models.CharField(max_length=255, blank=True, null=True, 
                                 help_text="Шлях до зображення у статичних файлах")
    
    # Відносини
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)
    specifications = models.ManyToManyField(ProductSpecification, blank=True)
    images = models.ManyToManyField(ProductImage)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def main_image(self):
        """Повертає шлях до головного зображення"""
        return self.image_path
    
    def get_absolute_url(self):
        return f"/product/{self.slug}/"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        
        if self.old_price and self.price < self.old_price:
            self.discount = round((1 - (self.price / self.old_price)) * 100)
        super().save(*args, **kwargs)

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review by {self.user.username} for {self.product.name}"

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='user_avatars/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    GENDER_CHOICES = [
        ('M', 'Чоловік'),
        ('F', 'Жінка'),
        ('O', 'Інше'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    
    def __str__(self):
        return f"Profile of {self.user.username}"

class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addresses')
    name = models.CharField(max_length=100)  # Назва адреси (Дім, Робота тощо)
    recipient = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    address = models.TextField()
    postal_code = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} - {self.city}, {self.address}"

class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'product')
    
    def __str__(self):
        return f"{self.user.username}'s wishlist item: {self.product.name}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Очікує обробки'),
        ('processing', 'В обробці'),
        ('shipped', 'Відправлено'),
        ('delivered', 'Доставлено'),
        ('cancelled', 'Скасовано'),
    ]
    PAYMENT_CHOICES = [
        ('cash_on_delivery', 'Готівкою при отриманні'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True, default='temp')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_CHOICES,
        default='cash_on_delivery'
    )
    nova_poshta_city = models.CharField(max_length=100, blank=True, null=True)
    nova_poshta_city_ref = models.CharField(max_length=100, blank=True, null=True)
    nova_poshta_department = models.CharField(max_length=100, blank=True, null=True)
    nova_poshta_department_name = models.CharField(max_length=255, blank=True, null=True)
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=20)
    customer_email = models.EmailField()
    
    def __str__(self):
        return f'Order #{self.order_number}'
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate order number: YYMMDD + random 4 digits
            date_str = timezone.now().strftime('%y%m%d')
            random_str = ''.join(random.choices('0123456789', k=4))
            self.order_number = f'{date_str}{random_str}'
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created_at']
    
    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Ціна на момент замовлення
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order #{self.order.order_number})"
    
    @property
    def total_price(self):
        return self.price * self.quantity

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email є обов'язковим!")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email.split('@')[0]
        super().save(*args, **kwargs)
        
class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def total_price(self):
        return self.product.price * self.quantity
    
    @property
    def image_url(self):
        return self.product.main_image.url
    
    def to_dict(self):
        return {
            'id': self.product.id,
            'name': self.product.name,
            'price': float(self.product.price),
            'quantity': self.quantity,
            'image': self.product.main_image.url
        }
    
    class Meta:
        verbose_name = 'Товар у кошику'
        verbose_name_plural = 'Товари у кошику'
        unique_together = ('user', 'product')
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.quantity})"