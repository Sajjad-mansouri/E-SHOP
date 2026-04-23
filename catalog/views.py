from datetime import timedelta
from decimal import Decimal
from collections import defaultdict
from django.shortcuts import render, get_object_or_404
from django.views.generic.base import View, TemplateResponseMixin
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.db.models import Q, Sum, Prefetch
from django.http import JsonResponse
from django.db.models import Avg, Max, Case, When, Value, CharField, F
from django.db.models.functions import Cast
from django.utils import timezone

from catalog.models import Category, Product, UserRating, ProductAttributeValue, ProductAttribute, ProductClass
from stock.models import StockRecord
from comment.forms import CommentForm
from cart.forms import CartItemForm
from offer.models import Offer,OfferApplication
from comment.models import Comment
from collection.models import CollectionList, ProductList
from . import mixins
from .utils import get_constant_attr_q

CONSTANT_ATTR = ["price_min", "price_max", "availability", "rating", "brand", "color"]

class HomePageView(TemplateResponseMixin, View):
	template_name = "catalog/list/home2.html"
	def get(self, request, *args, **kwargs):

				

		stock_records = self.get_trending_products()

		categories = Category.objects.filter(depth=1)
		collections = CollectionList.objects.filter(status="active")
		context = {

					"stock_records":stock_records,
					"collections":collections,
					"categories":categories
					}
		return self.render_to_response(context)

	def get_trending_products(self, product_count=5, period=30):

		start = timezone.now() - timedelta(days=period)
		product_selling_q = (Q(stock_carts__cart__order__created_at__gte=start)
			)
		q = Q(stock_carts__cart__order__status__in=["pending", "processing", "shipped","delivered"]) & product_selling_q
		top_selling = StockRecord.objects.annotate(sell_count = Sum("stock_carts__quantity", filter=q))	
		top_selling = top_selling.order_by("-sell_count")
		return top_selling

class ProductDetailView(DetailView):
	model = Product
	template_name = "catalog/detail/product.html"

	def get_context_data(self,**kwargs):

		context = super().get_context_data(**kwargs)
		stock_record_id = self.kwargs.get("stock_id")
		stock_record = get_object_or_404(StockRecord, id=stock_record_id)
		attributes_values = self.get_attribute_values()
		comment_form = CommentForm(initial={'stock_record':stock_record})


		product_ratings = Comment.objects.filter(stockrecord=stock_record).aggregate(rating_mean=Avg("rating", default=0))
		product_ratings_count = Comment.objects.filter(stockrecord=stock_record).distinct().count()


		context["stock_record"] = stock_record
		context["attributes_values"] = attributes_values
		context["comment_form"]=comment_form
		context["cart_form"] = CartItemForm()

		context["product_ratings"] = product_ratings["rating_mean"]
		context["product_ratings_count"] = product_ratings_count


		return context

	def get_attribute_values(self):
		attributes_values = []
		for attribute in self.object.product_attributes.all():
			attribute_type = attribute.attribute.type
			if attribute_type == 'text':
				if attribute.value_text:
					attributes_values.append((f"{attribute.attribute}", attribute.value_text))
			


		return attributes_values


class CategoryProducts(mixins.AjaxSortingResponse, mixins.StockContexMixin, ListView):
	model = StockRecord
	template_name = "catalog/category/products.html"
	AJAX_template_name = "catalog/category/_products.html"
	paginate_by = 1


	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		breadcrumb = self.object.get_ancestors()
		breadcrumb = list(breadcrumb) + [self.object]
		attributes = self.get_attribute_values()
		context["breadcrumb"] = breadcrumb
		context['category'] = self.object
		context['attributes'] = attributes
		context['product_class'] = self.object.product_class


		return context
	def get_queryset(self):
		stock_records = super().get_queryset()
		category_slug = self.kwargs.get("slug")
		self.object = Category.objects.get(slug=category_slug)
		stock_records = self.get_stocks(stock_records)
		return stock_records

	def get_stocks(self, stock_records):
		descendants = self.object.get_descendants(include_self=True)
		stocks = stock_records.filter(product__category__in=descendants).distinct()

		stocks = self.apply_filter(stocks)
		stocks = self.apply_sorting(stocks)
		return stocks

	def apply_filter(self, stocks):
		q = self.get_filter()
		stocks = stocks.filter(q)
		return stocks

	def get_filter(self):
		q_total=Q()

		for key, values in self.request.GET.lists():

			if key  in CONSTANT_ATTR:
					q_sub=Q()
					for value in values:
						q= get_constant_attr_q(key, value)
						q_sub = q_sub|q
					q_total = q_total & q_sub

			else:
				try:
					if self.object.product_class:
						q_sub=Q()

						for value in values:
							product_class = ProductClass.objects.get(id=self.object.product_class.id)
							product_attribute = ProductAttribute.objects.get(name=key, product_class=product_class)
							value_type = product_attribute.type
							q = self.get_q(value_type, value)
							q_sub = q_sub|q

						q_total = q_total & q_sub


				except (ProductAttribute.DoesNotExist, ProductClass.DoesNotExist) as e:
					pass

		return q_total

	def get_q(self, value_type, value):

		QUERY = {
			"text":Q(product__product_attributes__value_text=value),
			"decimal":Q(product__product_attributes__value_decimal=value),
			"integer":Q(product__product_attributes__value_integer=value),
			"boolean":Q(product__product_attributes__value_boolean=value),
			"float":Q(product__product_attributes__value_float=value),
			"richtext":Q(product__product_attributes__value_richtext=value),
			"date":Q(product__product_attributes__value_date=value),
			"datetime":Q(product__product_attributes__value_datetime=value),
			"file":Q(product__product_attributes__value_file=value),
			"image":Q(product__product_attributes__value_image=value),

		}
		return QUERY[value_type]


	def get_attribute_value_field(self, attr_type):
		ATTR_TYPE= {
		"text":"value_text"
		}
		return ATTR_TYPE[attr_type]

	def get_attribute_values(self):

		if self.object.product_class:
			# attributes =  (self.object.product_class.attributes.all()
			# 				.prefetch_related(Prefetch("attribute_values", to_attr="values"))
			# 	)
			qs = ProductAttributeValue.objects.filter(attribute__product_class=self.object.product_class).select_related("attribute")
			qs = qs.annotate(value_display = Case(
				When(attribute__type="text", then=F("value_text")),
				When(attribute__type="decimal", then=Cast("value_decimal", CharField())),
				When(attribute__type="boolean", then=Cast("value_boolean", CharField())),


				default=Value("")
				)).values("attribute__name", "value_display").distinct()
			attributes = defaultdict(list)
			for item in qs:
				if item["value_display"]:
					attributes[item["attribute__name"]].append(item["value_display"])
			attributes = dict(attributes)
		else:
			attributes = ""


		return attributes





class ApplyRating(View):
	def post(self, request, *args, **kwargs):

		rating = int(request.POST.get("rating"))
		product_id = request.POST.get("product_id")
		try:
			product = Product.objects.get(id=product_id)
		except Product.DoesNotExist:
			return JsonResponse({"status":False})

		try:
			user_rating = UserRating.objects.get(user=request.user, product=product)
			user_rating.rating = rating
			user_rating.save()
		except UserRating.DoesNotExist:
			UserRating.objects.create(user=request.user, product=product, rating=rating)
		return JsonResponse({"status":True})

class OfferProductListView(mixins.AjaxSortingResponse, mixins.StockContexMixin, ListView):
	model = Offer
	template_name = "catalog/offer/products.html"
	AJAX_template_name = "catalog/offer/_products.html"
	paginate_by = 4


	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["categories"] = Category.objects.filter(depth=1)
		context["object"] = self.object
		return context
	def get_queryset(self):
		q = super().get_queryset()
		slug = self.kwargs.get("slug")
		self.object = get_object_or_404(q, slug=slug, status="active")
		stocks = self.get_stocks()
		return stocks



	def get_stocks(self):
		stocks = StockRecord.objects.filter(offer_apps__offer=self.object, offer_apps__is_accepted=True)
		stocks = self.apply_filter(stocks)
		stocks = self.apply_sorting(stocks)

		return stocks

	def apply_filter(self, stocks):
		q = self.get_filter()
		stocks = stocks.filter(q)
		return stocks

	def get_filter(self):

		category = self.request.GET.get("category")
		q_total=Q()

		for key, values in self.request.GET.lists():

			if key  in CONSTANT_ATTR:
					q_sub=Q()
					for value in values:
						q= get_constant_attr_q(key, value)
						q_sub = q_sub|q
					q_total = q_total & q_sub

		try:
			category = int(category)
			category_obj = Category.objects.get(id=category)
			descendant_ids = category_obj.get_descendants(include_self=True).values_list("id", flat=True)
			q_total = q_total & Q(product__category_id__in=descendant_ids)
		except Exception as e:
			pass


		return q_total



class CollectionListView(DetailView):
	model = CollectionList
	template_name = "catalog/collection/collection.html"


class SubCategoryListView(DetailView):
	model = Category
	template_name = "catalog/category/sub_categories.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["categories"] = self.object.get_children()
		return context


class ProductGroupListView(mixins.AjaxSortingResponse, mixins.StockContexMixin, ListView):
	model = ProductList
	template_name = "catalog/collection/product_group/products.html"
	AJAX_template_name = "catalog/collection/product_group/_products.html"
	paginate_by = 4


	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["object"] = self.object
		return context
	def get_queryset(self):
		q = super().get_queryset()
		slug = self.kwargs.get("slug")
		self.object = get_object_or_404(q, slug=slug, status="active")
		stocks = self.get_stocks()
		return stocks



	def get_stocks(self):
		stocks = self.object.get_stocks
		stocks = self.apply_filter(stocks)
		stocks = self.apply_sorting(stocks)

		return stocks

	def apply_filter(self, stocks):
		q = self.get_filter()
		stocks = stocks.filter(q)
		return stocks

	def get_filter(self):
		q_total=Q()

		for key, values in self.request.GET.lists():

			if key  in CONSTANT_ATTR:
					q_sub=Q()
					for value in values:
						q= get_constant_attr_q(key, value)
						q_sub = q_sub|q
					q_total = q_total & q_sub



		return q_total

