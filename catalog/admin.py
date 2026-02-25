from django.contrib import admin
from treebeard.forms import movenodeform_factory
from .models import ProductClass, Category, Product, ProductCategory, ProductAttribute, ProductAttributeValue


@admin.register(ProductClass)
class ProductClassAdmin(admin.ModelAdmin):
	list_display = ["name", "slug"]

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	form = movenodeform_factory(Category)
	list_display = ["name", "slug"]



@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = ['title', 'slug', 'created', 'updated']

admin.site.register(ProductCategory)
admin.site.register(ProductAttribute)
admin.site.register(ProductAttributeValue)
