from django.db import models
from django.contrib.auth.models import User, AbstractUser, Group, Permission
from django.conf import settings




CATEGORY_CHOICES = [
    ("keyboard", "Клавіатура"),
    ("mouse", "Миша"),
    ("headsets", "Гарнітура"),
]

from django.db import models

CATEGORY_CHOICES = [
    ("keyboard", "Клавіатура"),
    ("mouse", "Мишка"),
    ("headsets", "Гарнітури"),
]

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)  # Запас товару
    image_url = models.ImageField(upload_to='product_images/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    size = models.IntegerField(default=75)
    bundle = models.JSONField(default=list)  # Комплектація
    switches = models.CharField(max_length=100, default="Невідомо")
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default="keyboard")  # Поле з вибором
    type = models.CharField(max_length=100, default="")  # Поле "Тип"
    backlight = models.CharField(max_length=100, default="")
    connection = models.CharField(max_length=100, default="")
    battery_life = models.IntegerField(default=0)  # Час роботи у годинах
    components = models.TextField(default="Навушники, Кабель, USB-приймач, Інструкція")  # Комплектація

    def get_components(self):
        """Розбиває рядок `components` на список"""
        return self.components.split(", ")

    def __str__(self):
        return self.name



    def __str__(self):
        return self.name

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.quantity})"
    



from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

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
    username = models.CharField(max_length=150, unique=True)
    
    objects = CustomUserManager()  # 🔹 Додаємо кастомний менеджер

class Meta:
    app_label = "products"  # 🔹 Вказуємо додаток, до якого належить модель





class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status_choices = [
        ("processing", "В обробці"),
        ("shipped", "Відправлено"),
        ("delivered", "Доставлено"),
    ]
    status = models.CharField(max_length=20, choices=status_choices, default="processing")

    def __str__(self):
        return f"Замовлення №{self.id} ({self.get_status_display()})"
