from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    sku = models.CharField(max_length=64, unique=True)  # ✅ new

    description = models.TextField(blank=True)

    # store cents as int (best for Stripe)
    price_cents = models.PositiveIntegerField()

    active = models.BooleanField(default=True)
    image = models.ImageField(upload_to="products/", blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.sku})"


class Inventory(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="inventory")
    stock_on_hand = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.sku}: {self.stock_on_hand}"
