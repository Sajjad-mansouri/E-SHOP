from django.contrib import admin
from .models import ProductClass


@admin.register(ProductClass)
class ProductClassAdmin(admin.ModelAdmin):
	list_display = ["name", "slug"]
