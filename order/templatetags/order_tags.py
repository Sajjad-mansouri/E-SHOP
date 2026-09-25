from decimal import Decimal

from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def shipping_cost(context, shipping_method, cart):
    if shipping_method.free_shipping:
        if cart.get_items_price > shipping_method.free_shipping_threshold:
            return Decimal("0.0")
        else:
            return shipping_method.price
