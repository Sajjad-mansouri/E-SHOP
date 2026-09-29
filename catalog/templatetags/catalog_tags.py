from django import template
from django.db.models import Avg, Q

from cart.models import Cart
from catalog.models import Category, Product, UserRating
from offer.models import OfferApplication
from stock.models import StockRecord

register = template.Library()


@register.simple_tag(takes_context=True)
def is_bookmarked(context, stock_record):
    user = context["user"]
    # stock_record = context["stock_record"]
    if not user.is_authenticated:
        return False
    try:
        cart = Cart.objects.get(user=user, submited=False)
    except Cart.DoesNotExist:
        return False
    return cart.items.filter(stock=stock_record).exists()


@register.inclusion_tag("catalog/list/_pagination.html", takes_context=True)
def paginate(context):
    page_obj = context["page_obj"]
    paginator = context["paginator"]

    end_pages = paginator.page_range[-2:]
    first_pages = paginator.page_range[0:2]

    min_num = max(0, page_obj.number - 3)
    current_pages = paginator.page_range[min_num : page_obj.number + 2]
    first_pages = [number for number in first_pages if number not in current_pages]
    end_pages = [number for number in end_pages if number not in current_pages]

    return {
        "first_pages": first_pages,
        "current_pages": current_pages,
        "end_pages": end_pages,
        "page_obj": page_obj,
    }


@register.simple_tag(takes_context=True)
def product_rating(context, product_id):
    try:
        product = Product.objects.get(id=product_id)
        product_ratings = UserRating.objects.filter(product=product).aggregate(
            rating_mean=Avg("rating", default=0)
        )["rating_mean"]

    except Product.DoesNotExist:
        product_ratings = 0

    return product_ratings


@register.simple_tag(takes_context=True)
def product_rating_count(context, product_id):
    try:
        product = Product.objects.get(id=product_id)
        product_ratings_count = (
            UserRating.objects.filter(product=product).distinct().count()
        )
    except Product.DoesNotExist:
        product_ratings_count = 0

    return product_ratings_count


@register.inclusion_tag("catalog/partial/_breadcrumb.html", takes_context=True)
def get_product_breadcrumb(context, product=None, category=None):
    if product:
        category = product.category
    if category:
        breadcrumb = category.get_ancestors()
        breadcrumb = list(breadcrumb) + [category]
    else:
        breadcrumb = None
    return {"breadcrumb": breadcrumb, "product": product}


@register.filter
def humanize_timedelta(value):
    if not value:
        return ""
    days = value.days
    seconds = value.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    text = ""
    if days:
        text += f"{days}d "
    if hours:
        text += f"{hours}h "
    if minutes:
        text += f"{minutes}m "
    return text


@register.inclusion_tag("catalog/offer/_banner.html", takes_context=True)
def get_offer_banner(context, offers, priority):
    return {"offers": offers, "priority": priority}


@register.inclusion_tag("catalog/detail/_comment_star.html")
def render_comment_star(comment):
    try:
        rating = int(comment.rating)
    except ValueError:
        rating = 0
    return {"ratings": range(rating)}


@register.simple_tag()
def count_review_rection(review, action):
    if action == "like":
        return review.review_reactions.filter(like=True).count()
    elif action == "unlike":
        return review.review_reactions.filter(unlike=True).count()


@register.simple_tag(takes_context=True)
def has_reaction(context, review, action):
    user = context["user"]
    if not user.is_authenticated:
        return ""
    if action == "like":
        if review.review_reactions.filter(user=user, like=True).exists():
            return "selected"
    elif action == "unlike":
        if review.review_reactions.filter(user=user, unlike=True).exists():
            return "selected"


@register.simple_tag(takes_context=True)
def is_selected_ordering(context, sort_by):
    order_by = context["order_by"]

    if order_by == sort_by:
        return "selected"


@register.inclusion_tag("catalog/partial/_navbar.html", takes_context=True)
def get_navbar(context):
    request = context.get("request")

    current_slug = None
    if (
        request
        and request.resolver_match
        and request.resolver_match.url_name == "category_products"
    ):
        current_slug = request.resolver_match.kwargs.get("slug")

    active_slugs = set()
    active_root_slug = None

    if current_slug:
        try:
            current = Category.objects.get(slug=current_slug)

            for node in current.get_ancestors():
                active_slugs.add(node.slug)
            active_slugs.add(current.slug)

            root = current.get_root()
            active_root_slug = root.slug
            active_slugs.add(root.slug)

        except Category.DoesNotExist:
            pass

    categories = Category.get_root_nodes()

    return {
        "categories": categories,
        "active_slugs": active_slugs,
        "active_root_slug": active_root_slug,
        "request": request,
    }


@register.inclusion_tag("catalog/partial/_offer.html")
def get_offer_apps(offer_name):
    q = Q(offer__status="active") & Q(offer__name=offer_name) & Q(is_accepted=True)
    offer_apps = OfferApplication.objects.filter(q)
    return {"offer_apps": offer_apps, "offer_name": offer_name}


@register.inclusion_tag("catalog/category/_category_products.html")
def category_products(category):
    q = Q(status="public") & Q(product__category=category)
    stocks = StockRecord.objects.filter(q)
    return {"stocks": stocks[:5], "category": category}


@register.simple_tag(takes_context=True)
def get_search_kwarg(context):
    request = context["request"]
    return request.GET.get("search", "")
