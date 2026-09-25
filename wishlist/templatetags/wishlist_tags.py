from django import template

from wishlist.models import WishList

register = template.Library()


@register.simple_tag(takes_context=True)
def user_has_wishlist(context):
    user = context["user"]
    if not user.is_authenticated:
        return False
    stock_record = context["stock_record"]

    return WishList.objects.filter(user=user, stock_record=stock_record).exists()
