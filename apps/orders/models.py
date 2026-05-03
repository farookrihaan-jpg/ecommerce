from django.db import models
import uuid


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending',    'Pending'),
        ('confirmed',  'Confirmed'),
        ('processing', 'Processing'),
        ('shipped',    'Shipped'),
        ('delivered',  'Delivered'),
        ('cancelled',  'Cancelled'),
        ('refunded',   'Refunded'),
    ]

    order_number     = models.CharField(max_length=32, unique=True, editable=False)
    user             = models.ForeignKey('users.User', on_delete=models.PROTECT, related_name='orders')
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Snapshot of shipping address at time of order
    shipping_name    = models.CharField(max_length=100)
    shipping_line1   = models.CharField(max_length=255)
    shipping_line2   = models.CharField(max_length=255, blank=True)
    shipping_city    = models.CharField(max_length=100)
    shipping_state   = models.CharField(max_length=100)
    shipping_postal  = models.CharField(max_length=20)
    shipping_country = models.CharField(max_length=2, default='US')

    subtotal         = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost    = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax              = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total            = models.DecimalField(max_digits=10, decimal_places=2)

    notes            = models.TextField(blank=True)
    tracking_number  = models.CharField(max_length=100, blank=True)

    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Order #{self.order_number}'

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = uuid.uuid4().hex[:12].upper()
        super().save(*args, **kwargs)

    def cancel(self):
        if self.status in ('pending', 'confirmed'):
            # Restock items
            for item in self.items.all():
                item.variant.stock += item.quantity
                item.variant.save()
            self.status = 'cancelled'
            self.save()
            return True
        return False


class OrderItem(models.Model):
    order        = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    variant      = models.ForeignKey('products.ProductVariant', on_delete=models.PROTECT)
    product_name = models.CharField(max_length=255)  # snapshot
    variant_sku  = models.CharField(max_length=120)  # snapshot
    quantity     = models.PositiveIntegerField()
    unit_price   = models.DecimalField(max_digits=10, decimal_places=2)  # snapshot

    def __str__(self):
        return f'{self.quantity}x {self.product_name}'

    @property
    def subtotal(self):
        return self.unit_price * self.quantity
