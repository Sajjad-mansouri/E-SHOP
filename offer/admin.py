from django.contrib import admin

from .models import Offer, OfferApplication, OfferRange, OfferType


@admin.register(OfferRange)
class OfferRangeAdmin(admin.ModelAdmin):
    list_display = ["name", "description", "created"]


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "description",
        "status",
        "priority",
        "max_discount",
        "created",
    ]


admin.site.register(OfferType)
admin.site.register(OfferApplication)
