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
