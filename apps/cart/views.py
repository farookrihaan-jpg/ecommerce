from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from apps.products.models import ProductVariant


def get_or_create_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cart_detail(request):
    cart = get_or_create_cart(request.user)
    return Response(CartSerializer(cart).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    """
    Body: { "variant_id": <int>, "quantity": <int> }
    """
    variant_id = request.data.get('variant_id')
    quantity   = int(request.data.get('quantity', 1))

    try:
        variant = ProductVariant.objects.get(pk=variant_id)
    except ProductVariant.DoesNotExist:
        return Response({'error': 'Variant not found.'}, status=404)

    if quantity < 1:
        return Response({'error': 'Quantity must be at least 1.'}, status=400)

    cart = get_or_create_cart(request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, variant=variant)
    new_qty = quantity if created else item.quantity + quantity

    if new_qty > variant.stock:
        return Response({'error': f'Only {variant.stock} in stock.'}, status=400)

    item.quantity = new_qty
    item.save()

    return Response(CartSerializer(cart).data, status=201 if created else 200)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_cart_item(request, item_id):
    """
    Body: { "quantity": <int> }
    """
    quantity = int(request.data.get('quantity', 0))
    cart = get_or_create_cart(request.user)

    try:
        item = CartItem.objects.get(pk=item_id, cart=cart)
    except CartItem.DoesNotExist:
        return Response({'error': 'Item not found.'}, status=404)

    if quantity <= 0:
        item.delete()
        return Response({'message': 'Item removed.'}, status=200)

    if quantity > item.variant.stock:
        return Response({'error': f'Only {item.variant.stock} in stock.'}, status=400)

    item.quantity = quantity
    item.save()
    return Response(CartSerializer(cart).data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_from_cart(request, item_id):
    cart = get_or_create_cart(request.user)
    CartItem.objects.filter(pk=item_id, cart=cart).delete()
    return Response(CartSerializer(cart).data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_cart(request):
    cart = get_or_create_cart(request.user)
    cart.items.all().delete()
    return Response({'message': 'Cart cleared.'})
