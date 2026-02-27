from django.shortcuts import render
from django.views.generic.base import View, TemplateResponseMixin
from catalog.models import Category, Product


class HomePageView(TemplateResponseMixin, View):
	template_name = "catalog/list/home.html"
	def get(self, request, *args, **kwargs):
		categories = Category.objects.all()
		root_categories = []
		for category in categories:
			if category.is_root():
				root_categories.append(category)
				category.get_children()

		trending_products = self.get_trending_products()
		context = {"categories":root_categories, "trending_products":trending_products}
		return self.render_to_response(context)

	def get_trending_products(self, product_count=5):
		return Product.objects.order_by("-view_count")[:product_count]


