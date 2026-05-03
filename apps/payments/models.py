from django.db import models


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('succeeded', 'Succeeded'),
        ('failed',    'Failed'),
        ('refunded',  'Refunded'),
    ]

    order                 = models.OneToOneField('orders.Order', on_delete=models.PROTECT, related_name='payment')
    stripe_payment_intent = models.CharField(max_length=200, unique=True)
    stripe_charge_id      = models.CharField(max_length=200, blank=True)
    amount                = models.DecimalField(max_digits=10, decimal_places=2)
    currency              = models.CharField(max_length=3, default='usd')
    status                = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    failure_message       = models.TextField(blank=True)
    created_at            = models.DateTimeField(auto_now_add=True)
    updated_at            = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Payment {self.stripe_payment_intent} — {self.status}'
