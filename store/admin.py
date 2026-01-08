from django.contrib import admin
from django import forms
from .models import Product, Inventory, ProductImage

class ProductAdminForm(forms.ModelForm):
    price = forms.DecimalField(max_digits=10, decimal_places=2, required=True, help_text="USD")

    class Meta:
        model = Product
        fields = ["name", "description", 'slug',"image", "price_cents","scent_top", "scent_mid", "scent_base", "sku",]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["price"].initial = self.instance.price_cents / 100

    def clean_price(self):
        price = self.cleaned_data["price"]
        if price <= 0:
            raise forms.ValidationError("Price must be greater than 0.")
        return price

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.price_cents = int(round(self.cleaned_data["price"] * 100))
        if commit:
            obj.save()
        return obj

class InventoryInline(admin.StackedInline):
    model = Inventory
    extra = 0
    max_num = 1

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "alt_text", "sort_order", "is_active")
    ordering = ("sort_order",)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ("name", "sku", "price_cents", "inventory", "active")
    search_fields = ("name", "sku")
    inlines = [ProductImageInline,InventoryInline]

    fields = (
        "name", "slug", "sku",
        "description", "image",
        "price",
        "scent_top", "scent_mid", "scent_base",
        "active",
    )

