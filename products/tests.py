from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class UserAuthTestCase(TestCase):
    def setUp(self):
        """Створюємо тестового користувача перед виконанням тестів"""
        self.user = User.objects.create_user(username='testuser', password='securepassword123')

    def test_registration_success(self):
        """Перевіряємо успішну реєстрацію"""
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'strongpassword123',
            'password2': 'strongpassword123',
        })
        self.assertEqual(response.status_code, 302)  # Перенаправлення після успішної реєстрації
        self.assertTrue(User.objects.filter(username='newuser').exists())  # Користувач створений

    def test_registration_invalid_password(self):
        """Перевіряємо помилку при невідповідності паролів"""
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'strongpassword123',
            'password2': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)  # Форма не повинна перенаправляти
        self.assertFalse(User.objects.filter(username='newuser').exists())  # Користувач НЕ створений

    def test_login_success(self):
        """Перевіряємо вхід з правильними даними"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'securepassword123',
        })
        self.assertEqual(response.status_code, 302)  # Перенаправлення після успішного входу

    def test_login_invalid_credentials(self):
        """Перевіряємо помилку при неправильному паролі"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)  # Вхід неуспішний
        self.assertContains(response, "Неправильний пароль")  # Очікуємо повідомлення про помилку