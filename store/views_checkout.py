import stripe
from django.conf import settings
from django.db import transaction
from django.shortcuts import render, redirect
from django.urls import reverse
import json
import os
from store.cart import Cart
from store.models import Product
from orders.models import Order, OrderItem
from orders.forms import GuestCheckoutForm

stripe.api_key = settings.STRIPE_SECRET_KEY

# Simple flat shipping for now (change later)
FLAT_SHIPPING_CENTS = 0

def _build_cart_lines(request):
    cart = Cart(request)
    lines = []
    subtotal_cents = 0

    # Validate products + compute totals
    for pid, entry in cart.cart["items"].items():
        product = Product.objects.filter(id=int(pid), active=True).select_related("inventory").first()
        if not product:
            continue

        qty = int(entry["qty"])
        if qty <= 0:
            continue

        # stock check
        stock = getattr(product.inventory, "stock_on_hand", 0)
        if qty > stock:
            raise ValueError(f"Not enough stock for {product.name}. Requested {qty}, available {stock}.")

        line_total = product.price_cents * qty
        subtotal_cents += line_total
        lines.append((product, qty, line_total))

    if not lines:
        raise ValueError("Your cart is empty.")

    return lines, subtotal_cents

def checkout_start(request):
    cart = Cart(request)

    if request.method == "GET":
        form = GuestCheckoutForm()
        return render(request, "store/checkout.html", {"form": form})

    # POST
    form = GuestCheckoutForm(request.POST)
    if not form.is_valid():
        return render(request, "store/checkout.html", {"form": form})

    try:
        lines, subtotal_cents = _build_cart_lines(request)
    except ValueError as e:
        form.add_error(None, str(e))
        return render(request, "store/checkout.html", {"form": form})

    shipping_cents = FLAT_SHIPPING_CENTS
    tax_cents = 0  # keep 0 for MVP; add later
    total_cents = subtotal_cents + shipping_cents + tax_cents

    with transaction.atomic():
        order = Order.objects.create(
            status="PENDING",
            email=form.cleaned_data["email"],
            full_name=form.cleaned_data["full_name"],
            address1=form.cleaned_data["address1"],
            address2=form.cleaned_data["address2"],
            city=form.cleaned_data["city"],
            state=form.cleaned_data["state"],
            postal_code=form.cleaned_data["postal_code"],
            country=form.cleaned_data["country"],
            subtotal_cents=subtotal_cents,
            shipping_cents=shipping_cents,
            tax_cents=tax_cents,
            total_cents=total_cents,
        )

        for product, qty, line_total in lines:
            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                product_sku=product.sku,
                unit_price_cents=product.price_cents,
                quantity=qty,
            )

    # Build Stripe line_items (Stripe amounts in cents)
    stripe_line_items = [
        {
            "price_data": {
                "currency": "usd",
                "product_data": {"name": product.name},
                "unit_amount": product.price_cents,
            },
            "quantity": qty,
        }
        for product, qty, _ in lines
    ]

    # Add shipping as a line item (simple MVP)
    stripe_line_items.append({
        "price_data": {
            "currency": "usd",
            "product_data": {"name": "Shipping"},
            "unit_amount": shipping_cents,
        },
        "quantity": 1,
    })

    success_url = settings.SITE_URL + reverse("checkout_success") + "?session_id={CHECKOUT_SESSION_ID}"
    cancel_url = settings.SITE_URL + reverse("checkout_cancel")

    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=stripe_line_items,
        success_url=success_url,
        cancel_url=cancel_url,
        customer_email=order.email,
        metadata={"order_id": str(order.id)},
    )

    order.stripe_checkout_session_id = session.id
    order.save(update_fields=["stripe_checkout_session_id"])
    print(success_url)
    return redirect(session.url, permanent=False)

def checkout_success(request):
    # The webhook is what finalizes payment + inventory; this page is just UX.
    return render(request, "store/checkout_success.html")

def checkout_cancel(request):
    return render(request, "store/checkout_cancel.html")
