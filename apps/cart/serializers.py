# ── serializers.py ────────────────────────────────────────────────────────────
from rest_framework import serializers
from .models import Cart, CartItem
from apps.products.serializers import ProductVariantSerializer


class CartItemSerializer(serializers.ModelSerializer):
    variant  = ProductVariantSerializer(read_only=True)
    variant_id = serializers.IntegerField(write_only=True)
    subtotal   = serializers.ReadOnlyField()
    product_name  = serializers.CharField(source='variant.product.name', read_only=True)
    product_slug  = serializers.CharField(source='variant.product.slug', read_only=True)
    product_price = serializers.DecimalField(source='variant.product.price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model  = CartItem
        fields = ['id', 'variant', 'variant_id', 'quantity', 'subtotal', 'product_name', 'product_slug', 'product_price']


class CartSerializer(serializers.ModelSerializer):
    items      = CartItemSerializer(many=True, read_only=True)
    total      = serializers.ReadOnlyField()
    item_count = serializers.ReadOnlyField()

    class Meta:
        model  = Cart
        fields = ['id', 'items', 'total', 'item_count', 'updated_at']
