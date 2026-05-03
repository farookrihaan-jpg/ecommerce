from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.ReadOnlyField()

    class Meta:
        model  = OrderItem
        fields = ['id', 'product_name', 'variant_sku', 'quantity', 'unit_price', 'subtotal']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model  = Order
        fields = [
            'id', 'order_number', 'status',
            'shipping_name', 'shipping_line1', 'shipping_line2',
            'shipping_city', 'shipping_state', 'shipping_postal', 'shipping_country',
            'subtotal', 'shipping_cost', 'tax', 'total',
            'notes', 'tracking_number', 'items', 'created_at',
        ]
        read_only_fields = [
            'id', 'order_number', 'subtotal', 'total',
            'created_at', 'items',
        ]


class CreateOrderSerializer(serializers.Serializer):
    """Used to create an order from the current cart."""
    shipping_address_id = serializers.IntegerField()
    notes               = serializers.CharField(required=False, allow_blank=True)
