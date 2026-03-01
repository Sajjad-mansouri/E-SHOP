from django.shortcuts import render, get_object_or_404
from django.views.generic.base import View, TemplateResponseMixin
from django.views.generic.detail import DetailView
from catalog.models import Category, Product
from stock.models import StockRecord


class HomePageView(TemplateResponseMixin, View):
	template_name = "catalog/list/home.html"
	def get(self, request, *args, **kwargs):
		categories = Category.objects.all()
		root_categories = []
		for category in categories:
			if category.is_root():
				root_categories.append(category)
				category.get_children()

		stock_records = self.get_trending_products()
		context = {"categories":root_categories, "stock_records":stock_records}
		return self.render_to_response(context)

	def get_trending_products(self, product_count=5):
		return StockRecord.objects.filter(num_in_stock__gt=0)




class ProductDetailView(DetailView):
	model = Product
	template_name = "catalog/detail/product_detail.html"

	def get_context_data(self,**kwargs):

		context = super().get_context_data(**kwargs)
		stock_record_id = self.kwargs.get("stock_id")
		stock_record = get_object_or_404(StockRecord, id=stock_record_id)
		attributes_values = self.get_attribute_values()
		context["stock_record"] = stock_record
		context["attributes_values"] = attributes_values

		return context

	def get_attribute_values(self):
		attributes_values = []
		for attribute in self.object.product_attributes.all():
			attribute_type = attribute.attribute.type
			if attribute_type == 'text':
				attributes_values.append((f"{attribute}", attribute.value_text))


		return attributes_values