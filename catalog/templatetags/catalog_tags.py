from django import template
from cart.models import Cart

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