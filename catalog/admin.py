from django.contrib import admin
from treebeard.forms import movenodeform_factory
from treebeard.admin import TreeAdmin
from .models import (
					ProductClass, Category, Product, 
					ProductAttribute, 
					ProductAttributeValue, ProductImage,
					UserRating,ShortDescriptions

					)


@admin.register(ProductClass)
class ProductClassAdmin(admin.ModelAdmin):
	list_display = ["name", "slug"]


class CategoryAdmin(TreeAdmin):
	form = movenodeform_factory(Category)
	list_display = ["name", "slug"]



@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = ['pk','title', 'slug', 'created', 'updated']

admin.site.register(ShortDescriptions)
admin.site.register(ProductAttribute)
admin.site.register(ProductAttributeValue)
admin.site.register(ProductImage)
admin.site.register(Category,CategoryAdmin)


admin.site.register(UserRating)