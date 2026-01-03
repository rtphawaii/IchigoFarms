from django.contrib import admin
from django import forms
from .models import Product, Inventory

class ProductAdminForm(forms.ModelForm):
    price = forms.DecimalField(max_digits=10, decimal_places=2, required=True, help_text="USD")

    class Meta:
        model = Product
        fields = ("name", "slug", "sku", "description", "price", "active", "image")

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

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ("name", "sku", "price_cents","inventory", "active")
    search_fields = ("name", "sku")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [InventoryInline]
