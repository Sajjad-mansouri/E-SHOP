from django.contrib import admin

from .models import StockRecord


@admin.register(StockRecord)
class StockRecordAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "price",
        "get_type_of_discount",
        "get_discount",
        "get_final_price",
    ]
