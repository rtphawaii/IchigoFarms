from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=255, unique=True, blank=True, default="")

    sku = models.CharField(max_length=64, unique=True)  # ✅ new

    description = models.TextField(blank=True)

    # store cents as int (best for Stripe)
    price_cents = models.PositiveIntegerField()

    active = models.BooleanField(default=True)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    scent_top = models.CharField(max_length=255, blank=True, default="")
    scent_mid  = models.CharField(max_length=255, blank=True, default="")
    scent_base = models.CharField(max_length=255, blank=True, default="")

    def __str__(self):
        return f"{self.name} ({self.sku})"


class Inventory(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="inventory")
    stock_on_hand = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.sku}: {self.stock_on_hand}"


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        related_name="images",
        on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="products/")
    alt_text = models.CharField(max_length=200, blank=True, default="")
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.product.name} image #{self.sort_order}"
