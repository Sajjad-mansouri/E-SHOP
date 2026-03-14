from django.contrib import admin
from .models import OfferRange, OfferType, Offer


@admin.register(OfferRange)
class OfferRangeAdmin(admin.ModelAdmin):
	list_display = ["name", "description", "created"]

@admin.register(Offer)
class OfferRangeAdmin(admin.ModelAdmin):
	list_display = ["id", "name", "description", "status", "priority", "max_discount", "created"]

admin.site.register(OfferType)