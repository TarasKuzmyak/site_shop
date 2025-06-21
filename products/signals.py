from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Order

@receiver(post_save, sender=Order)
def send_admin_notification(sender, instance, created, **kwargs):
    if created:
        # Надсилання сповіщення адміністратору
        subject = f'Нове замовлення #{instance.id}'
        message = f'Нове замовлення від {instance.customer_name}\n\n' \
                  f'Деталі:\n' \
                  f'ID: {instance.id}\n' \
                  f'Сума: {instance.total_price} грн\n' \
                  f'Телефон: {instance.customer_phone}\n' \
                  f'Email: {instance.customer_email}\n' \
                  f'Адреса доставки: {instance.nova_poshta_city}, відділення {instance.nova_poshta_department}'
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],
            fail_silently=False,
        )