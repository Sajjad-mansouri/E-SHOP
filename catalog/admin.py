from django.contrib import admin
from treebeard.forms import movenodeform_factory
from treebeard.admin import TreeAdmin
from .models import ProductClass, Category, Product, ProductCategory, ProductAttribute, ProductAttributeValue, ProductImage


@admin.register(ProductClass)
class ProductClassAdmin(admin.ModelAdmin):
	list_display = ["name", "slug"]


class CategoryAdmin(TreeAdmin):
	form = movenodeform_factory(Category)
	list_display = ["name", "slug"]



@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = ['title', 'slug', 'created', 'updated']

admin.site.register(ProductCategory)
admin.site.register(ProductAttribute)
admin.site.register(ProductAttributeValue)
admin.site.register(ProductImage)
admin.site.register(Category,CategoryAdmin)


