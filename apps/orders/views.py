from decimal import Decimal
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Order, OrderItem
from .serializers import OrderSerializer, CreateOrderSerializer
from apps.cart.models import Cart
from apps.users.models import Address

TAX_RATE      = Decimal('0.08')   # 8%
SHIPPING_RATE = Decimal('10.00')  # flat rate; can add real logic
FREE_SHIPPING  = Decimal('200.00')


class OrderListView(generics.ListAPIView):
    serializer_class   = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items')


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class   = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_order(request):
    """
    Convert the user's cart into an Order.
    Body: { "shipping_address_id": <int>, "notes": "" }
    """
    serializer = CreateOrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    # Validate cart
    try:
        cart = Cart.objects.prefetch_related('items__variant__product').get(user=request.user)
    except Cart.DoesNotExist:
        return Response({'error': 'Cart not found.'}, status=400)

    if not cart.items.exists():
        return Response({'error': 'Your cart is empty.'}, status=400)

    # Validate address
    address = get_object_or_404(
        Address, pk=serializer.validated_data['shipping_address_id'], user=request.user
    )

    # Stock check + reserve
    for item in cart.items.all():
        if item.quantity > item.variant.stock:
            return Response(
                {'error': f'"{item.variant}" only has {item.variant.stock} left in stock.'},
                status=400
            )

    subtotal = cart.total
    shipping = Decimal('0') if subtotal >= FREE_SHIPPING else SHIPPING_RATE
    tax      = (subtotal + shipping) * TAX_RATE
    total    = subtotal + shipping + tax

    order = Order.objects.create(
        user             = request.user,
        status           = 'pending',
        shipping_name    = address.full_name,
        shipping_line1   = address.line1,
        shipping_line2   = address.line2,
        shipping_city    = address.city,
        shipping_state   = address.state,
        shipping_postal  = address.postal_code,
        shipping_country = address.country,
        subtotal         = subtotal,
        shipping_cost    = shipping,
        tax              = tax,
        total            = total,
        notes            = serializer.validated_data.get('notes', ''),
    )

    for item in cart.items.all():
        OrderItem.objects.create(
            order        = order,
            variant      = item.variant,
            product_name = item.variant.product.name,
            variant_sku  = item.variant.sku,
            quantity     = item.quantity,
            unit_price   = item.variant.product.price,
        )
        # Deduct stock
        item.variant.stock -= item.quantity
        item.variant.save()

    cart.items.all().delete()  # clear cart

    return Response(OrderSerializer(order).data, status=201)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cancel_order(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    if order.cancel():
        return Response({'message': 'Order cancelled.'})
    return Response({'error': 'This order cannot be cancelled.'}, status=400)
