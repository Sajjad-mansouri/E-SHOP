from django.contrib import admin
from .models import Cart,CartItem

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
	list_display = ["user", "date_created", "date_submitted", "get_items_price"]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
	list_display = ["cart", "stock", "quantity", "stock__price", "get_item_price"]
