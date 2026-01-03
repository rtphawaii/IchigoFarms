from django.contrib import admin, messages
from django.utils import timezone

from .models import Order, OrderItem
from .emails import send_order_shipped_email


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "quantity", "unit_price_cents", "line_total_cents")
    can_delete = False


@admin.action(description="Mark shipped + send tracking email")
def mark_shipped_and_email(modeladmin, request, queryset):
    count = 0
    for order in queryset:
        if order.status != Order.STATUS_PAID:
            continue

        if not order.tracking_number:
            messages.warning(request, f"Order {order.id}: missing tracking number.")
            continue

        order.mark_shipped()

        if order.shipped_email_sent_at is None:
            try:
                send_order_shipped_email(order)
                order.shipped_email_sent_at = timezone.now()
            except Exception as e:
                messages.error(request, f"Order {order.id}: failed to send shipped email ({e}).")
                continue

        order.save()
        count += 1

    messages.success(request, f"Marked shipped + emailed {count} orders.")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    @admin.display(description="Items", ordering=None)
    def total_items_display(self, obj):
        return obj.total_items
    list_display = ("id", "status", "email", "total_items_display", "total_cents", "carrier", "tracking_number", "shipped_at")
    list_filter = ("status", "carrier")
    search_fields = ("id", "email", "tracking_number")
    inlines = [OrderItemInline]
    actions = [mark_shipped_and_email]

    fieldsets = (
        ("Customer", {"fields": ("email", "full_name")}),
        ("Shipping Address", {"fields": ("address1", "address2", "city", "state", "postal_code", "country")}),
        ("Totals", {"fields": ("subtotal_cents", "shipping_cents", "tax_cents", "total_cents")}),
        ("Stripe", {"fields": ("stripe_checkout_session_id", "stripe_payment_intent_id")}),
        ("Tracking", {"fields": ("carrier", "tracking_number", "tracking_url")}),
        ("Lifecycle", {"fields": ("status", "paid_at", "shipped_at", "delivered_at")}),
        ("Email Flags", {"fields": ("confirmation_sent_at", "shipped_email_sent_at", "delivered_email_sent_at")}),
    )

    readonly_fields = (
        "total_items_display",
        "paid_at",
        "shipped_at",
        "delivered_at",
        "confirmation_sent_at",
        "shipped_email_sent_at",
        "delivered_email_sent_at",
    )

