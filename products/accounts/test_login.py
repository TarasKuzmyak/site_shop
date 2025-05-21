from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class UserLoginTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='securepassword123')

    def test_login_success(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'securepassword123',
        })
        self.assertEqual(response.status_code, 302)  # Перевіряємо перенаправлення після входу

    def test_login_invalid_credentials(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)  # Вхід неуспішний
        self.assertContains(response, "Неправильний пароль")  # Очікуємо повідомлення про помилку