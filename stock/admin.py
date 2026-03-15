from django.contrib import admin

from .models import StockRecord

@admin.register(StockRecord)
class StockRecordAdmin(admin.ModelAdmin):
	list_display = ['id']