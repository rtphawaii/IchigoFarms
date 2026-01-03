import stripe
from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from orders.emails import send_order_confirmation_email

from orders.models import Order
from store.models import Inventory

stripe.api_key = settings.STRIPE_SECRET_KEY

def _send_order_confirmation(order: Order):
    subject = f"Order Confirmation #{order.id}"
    lines = []
    for item in order.items.select_related("product").all():
        lines.append(f"- {item.product.name} x{item.quantity} (${item.unit_price_cents/100:.2f} each)")
    body = "\n".join([
        f"Thanks for your order, {order.full_name}!",
        "",
        f"Order #{order.id}",
        "",
        "Items:",
        *lines,
        "",
        f"Subtotal: ${order.subtotal_cents/100:.2f}",
        f"Shipping: ${order.shipping_cents/100:.2f}",
        f"Tax: ${order.tax_cents/100:.2f}",
        f"Total: ${order.total_cents/100:.2f}",
        "",
        "Shipping to:",
        order.address1,
        (order.address2 or ""),
        f"{order.city}, {order.state} {order.postal_code}",
        order.country,
        "",
        "If you have questions, just reply to this email.",
    ])

    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [order.email], fail_silently=False)

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except Exception:
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        order_id = session.get("metadata", {}).get("order_id")

        if order_id:
            with transaction.atomic():
                order = Order.objects.select_for_update().get(id=int(order_id))

                # Idempotency: if already paid, do nothing
                if order.status != "PAID":
                    order.status = "PAID"
                    order.stripe_payment_intent_id = session.get("payment_intent", "")
                    order.save(update_fields=["status", "stripe_payment_intent_id"])

                    # Decrement inventory safely
                    for item in order.items.select_related("product").all():
                        inv = Inventory.objects.select_for_update().get(product=item.product)
                        if inv.stock_on_hand < item.quantity:
                            # You can choose to flag for manual handling here
                            # but we won't error Stripe webhook to avoid retries loops.
                            continue
                        inv.stock_on_hand -= item.quantity
                        inv.save(update_fields=["stock_on_hand"])
                    
                    if order.confirmation_sent_at is None:
                        send_order_confirmation_email(order)
                        order.confirmation_sent_at = timezone.now()
                        order.save(update_fields=["confirmation_sent_at"])

            # Send email outside transaction (fine either way)
            try:
                _send_order_confirmation(order)
            except Exception:
                # In prod: log this
                pass

    return HttpResponse(status=200)
