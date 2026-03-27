from django.contrib import admin
from .models import Shipping

@admin.register(Shipping)
class ShippingAdmin(admin.ModelAdmin):
	list_display = ["id", 'shipping_type', "free_shipping", "delivery_time"]
