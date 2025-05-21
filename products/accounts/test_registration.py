from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

class UserRegistrationTestCase(TestCase):
    def test_registration_success(self):
        response = self.client.post(reverse('register'), {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'securepassword123',
            'password2': 'securepassword123',
        })
        self.assertEqual(response.status_code, 302)  # Перевіряємо перенаправлення
        self.assertTrue(User.objects.filter(username='testuser').exists())  # Користувач створений

    def test_registration_invalid_password(self):
        response = self.client.post(reverse('register'), {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'securepassword123',
            'password2': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)  # Помилка на сторінці реєстрації
        self.assertFalse(User.objects.filter(username='testuser').exists())  # Користувач НЕ створений