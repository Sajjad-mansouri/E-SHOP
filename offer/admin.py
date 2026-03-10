from django.contrib import admin
from .models import OfferRange


@admin.register(OfferRange)
class OfferRangeAdmin(admin.ModelAdmin):
	list_display = ["name", "description", "created"]