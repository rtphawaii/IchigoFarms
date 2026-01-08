from django.shortcuts import render, get_object_or_404
from .models import Product

def product_list(request):
    products = Product.objects.filter(active=True).select_related("inventory").prefetch_related("images")
    return render(request, "store/product_list.html", {"products": products})

def product_detail(request, slug):
    product = Product.objects.prefetch_related("images").get(slug=slug, active=True)
    return render(request, "store/product_detail.html", {"product": product})

import re

def parse_scent_profile(description: str):
    if not description:
        return "", None, None, None

    # Normalize newlines
    text = description.replace("\r\n", "\n").replace("\r", "\n")

    if "[Scent Profile]" not in text:
        return text, None, None, None

    main, profile = text.split("[Scent Profile]", 1)
    main = main.strip()

    def grab(label):
        m = re.search(rf"^{label}:\s*(.+)$", profile, flags=re.MULTILINE)
        return m.group(1).strip() if m else None

    top = grab("Top")
    mid = grab("Mid")
    base = grab("Base")

    return main, top, mid, base

