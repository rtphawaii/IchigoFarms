from django.conf import settings
from django.core.mail import send_mail


def send_order_confirmation_email(order):
    subject = f"Order Confirmation #{order.id}"

    lines = []
    for item in order.items.select_related("product").all():
        lines.append(f"- {item.product_name} x{item.quantity} (${item.unit_price_cents/100:.2f} each)")


    body = "\n".join([
        f"Thanks for your order, {order.full_name}!",
        "",
        f"Order #: {order.id}",
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
        "If you have questions, reply to this email.",
    ])

    send_mail(
        subject,
        body,
        settings.DEFAULT_FROM_EMAIL,
        [order.email],
        fail_silently=False,
    )


def send_order_shipped_email(order):
    subject = f"Your order #{order.id} has shipped"

    body = "\n".join([
        f"Hi {order.full_name},",
        "",
        f"Good news — your order #{order.id} has shipped.",
        "",
        f"Carrier: {order.carrier or '—'}",
        f"Tracking #: {order.tracking_number or '—'}",
        f"Tracking link: {order.tracking_url or '—'}",
        "",
        "Thanks!",
    ])

    send_mail(
        subject,
        body,
        settings.DEFAULT_FROM_EMAIL,
        [order.email],
        fail_silently=False,
    )
