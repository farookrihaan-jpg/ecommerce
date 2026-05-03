from django.db import models


class Cart(models.Model):
    """One cart per user (or anonymous session)."""
    user       = models.OneToOneField('users.User', on_delete=models.CASCADE, null=True, blank=True, related_name='cart')
    session_id = models.CharField(max_length=120, blank=True, null=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Cart({self.user or self.session_id})'

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def item_count(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart     = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    variant  = models.ForeignKey('products.ProductVariant', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'variant')

    def __str__(self):
        return f'{self.quantity}x {self.variant}'

    @property
    def subtotal(self):
        return self.variant.product.price * self.quantity

    def save(self, *args, **kwargs):
        if self.quantity > self.variant.stock:
            raise ValueError(f'Only {self.variant.stock} items in stock.')
        super().save(*args, **kwargs)
