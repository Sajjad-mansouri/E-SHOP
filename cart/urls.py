from django.urls import path
from .views import AddToCartView

app_name = "cart"

urlpatterns = [
	path('add_cart/', AddToCartView.as_view(), name='add_cart')
]