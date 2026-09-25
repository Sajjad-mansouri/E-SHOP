from decimal import Decimal

from django.db.models import Q


def get_constant_attr_q(key, value):
    """
    return filter for constant attribute between all products
    """
    if isinstance(value, Decimal):
        value = Decimal(value)

    if key == "price_min":
        q = Q(price__gte=value)

    elif key == "price_max":
        q = Q(price__lte=value)

    elif key == "availability":
        value = int(value)
        q = Q(num_in_stock__gte=value)
    elif key == "rating":
        value = float(value)
        q = Q(rating__gte=value)

    elif key == "brand":
        q = Q(product__brand=value)

    elif key == "color":
        q = Q(product__color=value)

    elif key == "search":
        q = (
            Q(product__title__icontains=value)
            | Q(product__brand__icontains=value)
            | Q(product__upc__icontains=value)
            | Q(sku__icontains=value)
        )
    else:
        q = Q()

    return q
