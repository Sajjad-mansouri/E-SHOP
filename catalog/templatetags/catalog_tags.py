from django import template
from django.db.models import Avg
from cart.models import Cart
from catalog.models import UserRating, Product

register = template.Library()

@register.simple_tag(takes_context=True)
def is_bookmarked(context):
	user = context["user"]
	stock_record = context["stock_record"]
	try:
		cart = Cart.objects.get(user=user)
	except Cart.DoesNotExist:
		return False
	return cart.items.filter(stock=stock_record).exists()

@register.inclusion_tag("catalog/list/_pagination.html",takes_context=True)
def paginate(context):
	page_obj = context['page_obj']
	paginator = context['paginator']

	end_pages = paginator.page_range[-2:]
	first_pages = paginator.page_range[0:2]

	min_num = max(0, page_obj.number-3)
	current_pages = paginator.page_range[min_num:page_obj.number+2]
	first_pages = [number for number in first_pages if number not in current_pages]
	end_pages = [number for number in end_pages if number not in current_pages]
	


	return {"first_pages":first_pages, "current_pages":current_pages, "end_pages":end_pages, "page_obj":page_obj}


@register.simple_tag(takes_context=True)
def product_rating(context, product_id):
	try:
		product = Product.objects.get(id=product_id)
		product_ratings = UserRating.objects.filter(product=product).aggregate(rating_mean=Avg("rating", default=0))["rating_mean"]

	except Product.DoesNotExist:
		product_ratings = 0

	return product_ratings

@register.simple_tag(takes_context=True)
def product_rating_count(context, product_id):
	try:
		product = Product.objects.get(id=product_id)
		product_ratings_count = UserRating.objects.filter(product=product).distinct().count()
	except Product.DoesNotExist:
		product_ratings_count = 0

	return product_ratings_count