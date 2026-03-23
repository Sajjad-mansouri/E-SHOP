from django.shortcuts import render, get_object_or_404
from django.views.generic.base import View, TemplateResponseMixin
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from catalog.models import Category, Product
from stock.models import StockRecord
from comment.forms import CommentForm
from cart.forms import CartItemForm

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
		comment_form = CommentForm(initial={'stock_record':stock_record})
		context["stock_record"] = stock_record
		context["attributes_values"] = attributes_values
		context['comment_form']=comment_form
		context['cart_form'] = CartItemForm()

		return context

	def get_attribute_values(self):
		attributes_values = []
		for attribute in self.object.product_attributes.all():
			attribute_type = attribute.attribute.type
			if attribute_type == 'text':
				attributes_values.append((f"{attribute}", attribute.value_text))


		return attributes_values


class CategoryProducts(ListView):
	model = Category
	template_name = "catalog/list/category_products.html"
	paginate_by = 1
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		breadcrumb = self.category.get_ancestors()
		breadcrumb = list(breadcrumb) + [self.category]
		context["breadcrumb"] = breadcrumb
		context['category'] = self.category
		return context

	def get_queryset(self):
		slug = self.kwargs.get("category")
		self.category = get_object_or_404(Category, slug=slug)
		descendants = self.category.get_descendants(include_self=True)
		stocks = StockRecord.objects.filter(product__categories__in=descendants).distinct()
		return stocks

