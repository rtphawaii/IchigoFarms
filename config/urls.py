from django.contrib import admin
from django.urls import path, include
from orders.views_webhook import stripe_webhook
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("store.urls")),
    path("webhooks/stripe/", stripe_webhook, name="stripe_webhook"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)