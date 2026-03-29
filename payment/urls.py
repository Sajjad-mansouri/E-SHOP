from django.urls import path
from .views import Checkout

app_name = "payment"
urlpatterns = [
	path("checkout/", Checkout.as_view(), name="checkout")
]