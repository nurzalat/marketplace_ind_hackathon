from django.contrib.auth import get_user_model
from django.db import models

from account.send_email import send_order_notification
from product.models import Product
from django.dispatch import receiver
from django.db.models.signals import post_save

User = get_user_model()

STATUS_CHOICES = (
    ('open', 'Open'),
    ('in_progress', 'Being processed'),
    ('closed', 'Closed'),
)


class Order(models.Model):
    user = models.ForeignKey(User, related_name='order_to_user', on_delete=models.RESTRICT)
    product = models.ManyToManyField(Product, through='OrderItem')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)


@receiver(post_save, sender=Order)
def order_post_save(sender, instance, *args, **kwargs):
    send_order_notification(instance.user, instance.id)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.RESTRICT)
    product = models.ForeignKey(Product, related_name='product_to_order', on_delete=models.RESTRICT)
    quantity = models.SmallIntegerField(default=1)
