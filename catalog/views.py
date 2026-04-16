from datetime import timedelta
from decimal import Decimal
from django.shortcuts import render, get_object_or_404
from django.views.generic.base import View, TemplateResponseMixin
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.db.models import Q, Sum, Prefetch
from django.http import JsonResponse
from django.db.models import Avg, Max
from django.utils import timezone

from catalog.models import Category, Product, UserRating, ProductAttributeValue, ProductAttribute, ProductClass
from stock.models import StockRecord
from comment.forms import CommentForm
from cart.forms import CartItemForm
from offer.models import Offer
from comment.models import Comment

class HomePageView(TemplateResponseMixin, View):
	template_name = "catalog/list/home.html"
	def get(self, request, *args, **kwargs):

				

		stock_records = self.get_trending_products()
		offers = Offer.objects.filter(status="open")
		context = {

					"stock_records":stock_records,
					"offers":offers,
					"now":timezone.now()
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


class CategoryProducts(ListView):
	model = StockRecord
	template_name = "catalog/category/products.html"
	paginate_by = 1

	def dispatch(self, request, *args, **kwargs):
		self.is_ajax = request.headers.get('AJAX')
		if self.is_ajax:
			self.template_name = "catalog/category/_products.html"

		return super().dispatch(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		breadcrumb = self.object.get_ancestors()
		breadcrumb = list(breadcrumb) + [self.object]
		attributes = self.get_attribute_values()

		agg =self.object_list.aggregate(max_price=Max("price"))
		max_price = agg["max_price"]
		context["breadcrumb"] = breadcrumb
		context['category'] = self.object
		context['attributes'] = attributes
		context['product_class'] = self.object.product_class
		context['max_price'] = max_price
		context['order_by'] = self.order_by






		return context
	def get_queryset(self):
		stock_records = super().get_queryset()
		category_slug = self.kwargs.get("slug")
		self.object = Category.objects.get(slug=category_slug)
		stock_records = self.get_stocks(stock_records)
		return stock_records

	def get_stocks(self, stock_records):
		descendants = self.object.get_descendants(include_self=True)
		stocks = stock_records.filter(product__categories__in=descendants).distinct()

		stocks = self.apply_filter(stocks)
		stocks = self.apply_sorting(stocks)
		return stocks

	def apply_filter(self, stocks):
		q = self.get_filter()
		stocks = stocks.filter(q)
		return stocks

	def get_filter(self):
		q_total=Q()
		for key, value in self.request.GET.items():

			if key  in ["price_min", "price_max", "availability", "rating"]:
				q= self.get_stock_q(key, value)
				q_total = q_total & q

			else:
				try:
					product_class = ProductClass.objects.get(id=self.object.product_class.id)
					product_attribute = ProductAttribute.objects.get(name=key, product_class=product_class)
					value_type = product_attribute.type
					q = self.get_q(value_type, value)
					q_total = q_total & q


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

	def get_stock_q(self, key, value):
		if isinstance(value, Decimal):
			value = Decimal(value)

		if key == "price_min":
			q = Q(price__gte=value)

		elif key == "price_max":

			q = Q(price__lte=value)

		elif key == "availability":
			
			q = Q(num_in_stock__gt=0)
		elif key == "rating":
			value = float(value)
			q = Q(rating__gte=value)


		return q

	def get_attribute_value_field(self, attr_type):
		ATTR_TYPE= {
		"text":"value_text"
		}
		return ATTR_TYPE[attr_type]

	def get_attribute_values(self):
		print(self.object)
		print(self.object.product_class)
		if self.object.product_class:
			attributes =  (self.object.product_class.attributes.all()
							.prefetch_related(Prefetch("attribute_values", to_attr="values"))
				)
		else:
			attributes = ""
		return attributes


	def apply_sorting(self, stocks):
		sort_by = self.get_order()
		stocks = stocks.order_by(*sort_by)
		return stocks

	def get_order(self):
		self.order_by = self.request.GET.get("sort-by", "best-selling")
		if self.order_by == "best-selling":
			sort_by = ["-sold"]

		elif self.order_by == "price-low":
			sort_by = ["price"]

		elif self.order_by == "price-high":
			sort_by = ["-price"]

		elif self.order_by == "rating":
			sort_by = ["-rating"]

		elif self.order_by == "newest":
			sort_by = ["date_created"]

		elif self.order_by == "oldest":
			sort_by = ["-date_created"]

		elif self.order_by == "discount":
			sort_by = ["-offer_discount", "-discount"]
		else:
			sort_by = ["-sold"]
		return sort_by
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

class OfferProductListView(DetailView):
	model = Offer
	template_name = "catalog/offer/products.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["offer_stocks"] = self.object.get_offer_products
		return context