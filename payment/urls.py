from django.urls import path

from .views import Checkout, CheckoutConfirmation

app_name = "payment"
urlpatterns = [
    path("checkout/", Checkout.as_view(), name="checkout"),
    path("checkout/confirmation/", CheckoutConfirmation.as_view(), name="confirmation"),
]
