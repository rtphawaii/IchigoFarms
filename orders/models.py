from django.db import models
from store.models import Product

from django.db import models
from django.utils import timezone


class Order(models.Model):
    @property
    def total_items(self) -> int:
        # total quantity across all order items
        return sum(self.items.values_list("quantity", flat=True))
    # ----------------------------
    # Status / lifecycle
    # ----------------------------
    STATUS_PENDING = "PENDING"
    STATUS_PAID = "PAID"
    STATUS_SHIPPED = "SHIPPED"
    STATUS_DELIVERED = "DELIVERED"
    STATUS_CANCELED = "CANCELED"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PAID, "Paid"),
        (STATUS_SHIPPED, "Shipped"),
        (STATUS_DELIVERED, "Delivered"),
        (STATUS_CANCELED, "Canceled"),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        db_index=True,
    )

    # ----------------------------
    # Customer + shipping address
    # ----------------------------
    email = models.EmailField()
    full_name = models.CharField(max_length=200)

    address1 = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=120)
    state = models.CharField(max_length=120)
    postal_code = models.CharField(max_length=40)
    country = models.CharField(max_length=2, default="US")

    # ----------------------------
    # Money (cents)
    # ----------------------------
    subtotal_cents = models.PositiveIntegerField(default=0)
    shipping_cents = models.PositiveIntegerField(default=0)
    tax_cents = models.PositiveIntegerField(default=0)
    total_cents = models.PositiveIntegerField(default=0)

    # ----------------------------
    # Stripe references
    # ----------------------------
    stripe_checkout_session_id = models.CharField(max_length=255, blank=True, db_index=True)
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, db_index=True)

    # ----------------------------
    # Tracking (manual entry)
    # ----------------------------
    carrier = models.CharField(max_length=50, blank=True)  # USPS/UPS/FedEx etc
    tracking_number = models.CharField(max_length=100, blank=True, db_index=True)
    tracking_url = models.URLField(blank=True)

    shipped_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)

    # ----------------------------
    # Timestamps
    # ----------------------------
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(blank=True, null=True)

    # ----------------------------
    # Email idempotency flags
    # ----------------------------
    confirmation_sent_at = models.DateTimeField(blank=True, null=True)
    shipped_email_sent_at = models.DateTimeField(blank=True, null=True)
    delivered_email_sent_at = models.DateTimeField(blank=True, null=True)

    # ----------------------------
    # Helpers
    # ----------------------------
    def mark_paid(self):
        self.status = self.STATUS_PAID
        if not self.paid_at:
            self.paid_at = timezone.now()

    def mark_shipped(self):
        self.status = self.STATUS_SHIPPED
        if not self.shipped_at:
            self.shipped_at = timezone.now()

    def mark_delivered(self):
        self.status = self.STATUS_DELIVERED
        if not self.delivered_at:
            self.delivered_at = timezone.now()

    def __str__(self):
        return f"Order #{self.id} ({self.status})"



class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price_cents = models.PositiveIntegerField()  # snapshot at purchase time
    line_total_cents = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"
