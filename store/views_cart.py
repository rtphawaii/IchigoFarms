from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_POST

from .models import Product
from .cart import Cart

FLAT_SHIPPING_CENTS = 0

def cart_detail(request):
    cart = Cart(request)
    items = []
    subtotal_cents = 0

    for pid, entry in cart.cart.get("items", {}).items():
        product = get_object_or_404(Product, id=int(pid), active=True)
        qty = int(entry.get("qty", 0))
        if qty <= 0:
            continue

        line_total = product.price_cents * qty
        subtotal_cents += line_total
        items.append({"product": product, "qty": qty, "line_total_cents": line_total})

    shipping_cents = FLAT_SHIPPING_CENTS if items else 0
    tax_cents = 0
    total_cents = subtotal_cents + shipping_cents + tax_cents

    return render(request, "store/cart_detail.html", {
        "items": items,
        "subtotal_cents": subtotal_cents,
        "shipping_cents": shipping_cents,
        "tax_cents": tax_cents,
        "total_cents": total_cents,
    })

@require_POST
def cart_add(request, product_id: int):
    cart = Cart(request)
    qty = int(request.POST.get("qty", 1))
    if qty < 1:
        qty = 1
    cart.add(product_id, qty=qty)
    return redirect("cart_detail")

@require_POST
def cart_set(request, product_id: int):
    cart = Cart(request)
    qty = int(request.POST.get("qty", 1))
    cart.set(product_id, qty=qty)
    return redirect("cart_detail")

@require_POST
def cart_remove(request, product_id: int):
    cart = Cart(request)
    cart.set(product_id, qty=0)
    return redirect("cart_detail")
