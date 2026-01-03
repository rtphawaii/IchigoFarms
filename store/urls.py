from django.urls import path
from . import views
from . import views_cart
from . import views_checkout

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("p/<slug:slug>/", views.product_detail, name="product_detail"),

    path("cart/", views_cart.cart_detail, name="cart_detail"),
    path("cart/add/<int:product_id>/", views_cart.cart_add, name="cart_add"),
    path("cart/set/<int:product_id>/", views_cart.cart_set, name="cart_set"),
    path("cart/remove/<int:product_id>/", views_cart.cart_remove, name="cart_remove"),

    path("checkout/", views_checkout.checkout_start, name="checkout_start"),
    path("checkout/success/", views_checkout.checkout_success, name="checkout_success"),
    path("checkout/cancel/", views_checkout.checkout_cancel, name="checkout_cancel"),
]
