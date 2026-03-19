from django.urls import path
from .views import AddToCartView, RemoveFromCartView, CartView

app_name = "cart"

urlpatterns = [
	path('add_cart/', AddToCartView.as_view(), name='add_cart_item'),
	path('remove_cart/', RemoveFromCartView.as_view(), name='remove_cart_item'),
	path('items/', CartView.as_view(), name='cart_items'),


]