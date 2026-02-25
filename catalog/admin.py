from django.contrib import admin
from treebeard.forms import movenodeform_factory
from .models import ProductClass, Category


@admin.register(ProductClass)
class ProductClassAdmin(admin.ModelAdmin):
	list_display = ["name", "slug"]

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	form = movenodeform_factory(Category)
	list_display = ["name", "slug"]



