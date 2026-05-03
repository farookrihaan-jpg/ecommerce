import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Payment
from apps.orders.models import Order

stripe.api_key = settings.STRIPE_SECRET_KEY


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_payment_intent(request):
    """
    Create a Stripe PaymentIntent for an order.
    Body: { "order_id": <int> }
    Returns: { "client_secret": "...", "payment_intent_id": "..." }
    """
    order_id = request.data.get('order_id')
    order    = get_object_or_404(Order, pk=order_id, user=request.user)

    if order.status not in ('pending', 'confirmed'):
        return Response({'error': 'Order is not payable.'}, status=400)

    if hasattr(order, 'payment') and order.payment.status == 'succeeded':
        return Response({'error': 'Order already paid.'}, status=400)

    amount_cents = int(order.total * 100)

    try:
        intent = stripe.PaymentIntent.create(
            amount   = amount_cents,
            currency = settings.STRIPE_CURRENCY,
            metadata = {
                'order_id':     order.id,
                'order_number': order.order_number,
                'user_id':      request.user.id,
            },
        )
    except stripe.error.StripeError as e:
        return Response({'error': str(e)}, status=400)

    # Create or update Payment record
    Payment.objects.update_or_create(
        order   = order,
        defaults={
            'stripe_payment_intent': intent.id,
            'amount':                order.total,
            'currency':              settings.STRIPE_CURRENCY,
            'status':                'pending',
        }
    )

    return Response({
        'client_secret':      intent.client_secret,
        'payment_intent_id':  intent.id,
        'amount':             order.total,
        'currency':           settings.STRIPE_CURRENCY,
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def confirm_payment(request):
    """
    Called after Stripe confirms payment on the frontend.
    Body: { "payment_intent_id": "pi_..." }
    """
    pi_id = request.data.get('payment_intent_id')
    if not pi_id:
        return Response({'error': 'payment_intent_id required.'}, status=400)

    try:
        intent = stripe.PaymentIntent.retrieve(pi_id)
    except stripe.error.StripeError as e:
        return Response({'error': str(e)}, status=400)

    try:
        payment = Payment.objects.get(stripe_payment_intent=pi_id)
    except Payment.DoesNotExist:
        return Response({'error': 'Payment record not found.'}, status=404)

    if intent.status == 'succeeded':
        payment.status          = 'succeeded'
        payment.stripe_charge_id = intent.latest_charge or ''
        payment.save()
        payment.order.status = 'confirmed'
        payment.order.save()
        return Response({'message': 'Payment confirmed.', 'order_number': payment.order.order_number})

    payment.status          = 'failed'
    payment.failure_message = intent.last_payment_error.message if intent.last_payment_error else 'Unknown error'
    payment.save()
    return Response({'error': 'Payment not completed.', 'stripe_status': intent.status}, status=400)


@csrf_exempt
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def stripe_webhook(request):
    """
    Stripe sends events here. Register this URL in your Stripe dashboard.
    """
    payload    = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return Response({'error': 'Invalid signature.'}, status=400)

    # ── Handle events ─────────────────────────────────────────────────────
    if event['type'] == 'payment_intent.succeeded':
        pi = event['data']['object']
        _handle_payment_succeeded(pi)

    elif event['type'] == 'payment_intent.payment_failed':
        pi = event['data']['object']
        _handle_payment_failed(pi)

    elif event['type'] == 'charge.refunded':
        charge = event['data']['object']
        _handle_refund(charge)

    return Response({'status': 'ok'})


# ── Internal handlers ─────────────────────────────────────────────────────────
def _handle_payment_succeeded(pi):
    try:
        payment = Payment.objects.get(stripe_payment_intent=pi['id'])
        payment.status           = 'succeeded'
        payment.stripe_charge_id = pi.get('latest_charge', '')
        payment.save()
        payment.order.status = 'confirmed'
        payment.order.save()
    except Payment.DoesNotExist:
        pass


def _handle_payment_failed(pi):
    try:
        payment = Payment.objects.get(stripe_payment_intent=pi['id'])
        payment.status          = 'failed'
        err = pi.get('last_payment_error')
        payment.failure_message = err['message'] if err else 'Unknown'
        payment.save()
    except Payment.DoesNotExist:
        pass


def _handle_refund(charge):
    try:
        payment = Payment.objects.get(stripe_charge_id=charge['id'])
        payment.status = 'refunded'
        payment.save()
        payment.order.status = 'refunded'
        payment.order.save()
    except Payment.DoesNotExist:
        pass
