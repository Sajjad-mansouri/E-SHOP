from collections import defaultdict
from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Case, CharField, Count, F, Q, Sum, Value, When
from django.db.models.functions import Cast, Coalesce
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic.base import TemplateResponseMixin, View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from cart.forms import CartItemForm
from catalog.models import (
    Category,
    Product,
    ProductAttribute,
    ProductAttributeValue,
    UserRating,
)
from collection.models import CollectionList, ProductList
from comment.forms import CommentForm
from comment.models import Comment
from offer.models import Offer
from stock.models import StockRecord

from . import mixins
from .utils import get_constant_attr_q

CONSTANT_ATTR = [
    "price_min",
    "price_max",
    "availability",
    "rating",
    "brand",
    "color",
    "search",
]


class HomePageView(TemplateResponseMixin, View):
    template_name = "catalog/list/home2.html"

    def get(self, request, *args, **kwargs):
        context = {
            "stock_records": self.get_trending_products(),
            "collections": CollectionList.objects.filter(status="active"),
            "categories": Category.objects.filter(depth=1),
        }
        return self.render_to_response(context)

    def get_trending_products(self, product_count=5, period=30):
        start = timezone.now() - timedelta(days=period)

        sales_filter = Q(order_items__order__created_at__gte=start) & Q(
            order_items__order__status__in=[
                "pending",
                "processing",
                "shipped",
                "delivered",
            ]
        )

        return StockRecord.objects.annotate(
            sell_count=Coalesce(
                Sum(
                    "order_items__quantity",
                    filter=sales_filter,
                ),
                Value(0),
            )
        ).order_by("-sell_count", "-date_created")[:product_count]


class ProductDetailView(DetailView):
    model = Product
    template_name = "catalog/detail/product.html"

    def get_stock_record(self):
        return get_object_or_404(
            StockRecord,
            pk=self.kwargs["stock_id"],
            product=self.object,
        )

    def get_attribute_values(self):
        attributes_values = []

        attributes = self.object.product_attributes.select_related(
            "attribute",
        )

        for attribute in attributes:
            if attribute.attribute.type == "text" and attribute.value_text:
                attributes_values.append(
                    (str(attribute.attribute), attribute.value_text),
                )

        return attributes_values

    def get_product_ratings(self, stock_record):
        return Comment.objects.filter(
            stockrecord=stock_record,
        ).aggregate(
            rating_mean=Avg("rating", default=0),
            rating_count=Count("id"),
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        stock_record = self.get_stock_record()
        ratings = self.get_product_ratings(stock_record)

        context.update(
            {
                "stock_record": stock_record,
                "attributes_values": self.get_attribute_values(),
                "comment_form": CommentForm(
                    initial={"stock_record": stock_record},
                ),
                "cart_form": CartItemForm(),
                "product_ratings": ratings["rating_mean"],
                "product_ratings_count": ratings["rating_count"],
            }
        )

        return context


class CategoryProducts(
    mixins.AjaxSortingResponse,
    mixins.StockContexMixin,
    ListView,
):
    model = StockRecord
    template_name = "catalog/category/products.html"
    AJAX_template_name = "catalog/category/_products.html"
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        breadcrumb = self.object.get_ancestors()
        breadcrumb = list(breadcrumb) + [self.object]

        context["breadcrumb"] = breadcrumb
        context["category"] = self.object
        context["attributes"] = self.get_attribute_values()
        context["product_class"] = self.object.product_class

        return context

    def get_queryset(self):
        stock_records = super().get_queryset()

        self.object = get_object_or_404(
            Category,
            slug=self.kwargs["slug"],
        )

        return self.get_stocks(stock_records)

    def get_stocks(self, stock_records):
        descendants = self.object.get_descendants(include_self=True)

        stocks = stock_records.filter(
            product__category__in=descendants,
        ).distinct()

        stocks = self.apply_filter(stocks)
        stocks = self.apply_sorting(stocks)

        return stocks

    def apply_filter(self, stocks):
        return stocks.filter(self.get_filter())

    def get_filter(self):
        q_total = Q()
        product_class = self.object.product_class

        for key, values in self.request.GET.lists():
            if key in CONSTANT_ATTR:
                q_sub = Q()

                for value in values:
                    q_sub |= get_constant_attr_q(key, value)

                q_total &= q_sub
                continue

            if not product_class:
                continue

            try:
                product_attribute = ProductAttribute.objects.get(
                    name=key,
                    product_class=product_class,
                )
            except ProductAttribute.DoesNotExist:
                continue

            q_sub = Q()

            for value in values:
                q_sub |= self.get_q(product_attribute, value)

            q_total &= q_sub

        return q_total

    def get_q(self, product_attribute, value):
        attribute_filter = Q(
            product__product_attributes__attribute=product_attribute,
        )

        value_filters = {
            "text": Q(
                product__product_attributes__value_text=value,
            ),
            "decimal": Q(
                product__product_attributes__value_decimal=value,
            ),
            "integer": Q(
                product__product_attributes__value_integer=value,
            ),
            "boolean": Q(
                product__product_attributes__value_boolean=value,
            ),
            "float": Q(
                product__product_attributes__value_float=value,
            ),
            "richtext": Q(
                product__product_attributes__value_richtext=value,
            ),
            "date": Q(
                product__product_attributes__value_date=value,
            ),
            "datetime": Q(
                product__product_attributes__value_datetime=value,
            ),
            "file": Q(
                product__product_attributes__value_file=value,
            ),
            "image": Q(
                product__product_attributes__value_image=value,
            ),
        }

        return attribute_filter & value_filters[product_attribute.type]

    def get_attribute_values(self):
        if not self.object.product_class:
            return ""

        qs = (
            ProductAttributeValue.objects.filter(
                attribute__product_class=self.object.product_class,
            )
            .select_related("attribute")
            .annotate(
                value_display=Case(
                    When(
                        attribute__type="text",
                        then=F("value_text"),
                    ),
                    When(
                        attribute__type="decimal",
                        then=Cast(
                            "value_decimal",
                            CharField(),
                        ),
                    ),
                    When(
                        attribute__type="boolean",
                        then=Cast(
                            "value_boolean",
                            CharField(),
                        ),
                    ),
                    default=Value(""),
                    output_field=CharField(),
                )
            )
            .values(
                "attribute__name",
                "value_display",
            )
            .distinct()
        )

        attributes = defaultdict(list)

        for item in qs:
            if item["value_display"]:
                attributes[item["attribute__name"]].append(
                    item["value_display"],
                )

        return dict(attributes)


class ApplyRating(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        product_id = request.POST.get("product_id")
        rating_value = request.POST.get("rating")

        if not product_id or not rating_value:
            return JsonResponse(
                {
                    "status": False,
                    "error": "product_id and rating are required.",
                },
                status=400,
            )

        try:
            product_id = int(product_id)
            rating = int(rating_value)
        except (TypeError, ValueError):
            return JsonResponse(
                {
                    "status": False,
                    "error": "product_id and rating must be integers.",
                },
                status=400,
            )

        if not 1 <= rating <= 5:
            return JsonResponse(
                {
                    "status": False,
                    "error": "Rating must be between 1 and 5.",
                },
                status=400,
            )

        try:
            Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return JsonResponse(
                {
                    "status": False,
                    "error": "Product not found.",
                },
                status=404,
            )

        UserRating.objects.update_or_create(
            user=request.user,
            product_id=product_id,
            defaults={"rating": rating},
        )

        return JsonResponse({"status": True})


class OfferProductListView(
    mixins.AjaxSortingResponse,
    mixins.StockContexMixin,
    ListView,
):
    model = Offer
    template_name = "catalog/offer/products.html"
    AJAX_template_name = "catalog/offer/_products.html"
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.filter(depth=1)
        context["object"] = self.object
        return context

    def get_queryset(self):
        offers = super().get_queryset()
        slug = self.kwargs["slug"]

        self.object = get_object_or_404(
            offers,
            slug=slug,
            status="active",
        )

        return self.get_stocks()

    def get_stocks(self):
        stocks = StockRecord.objects.filter(
            offer_apps__offer=self.object,
            offer_apps__is_accepted=True,
        ).distinct()

        stocks = self.apply_filter(stocks)
        stocks = self.apply_sorting(stocks)

        return stocks

    def apply_filter(self, stocks):
        return stocks.filter(self.get_filter())

    def get_filter(self):
        q_total = Q()

        for key, values in self.request.GET.lists():
            if key not in CONSTANT_ATTR:
                continue

            q_sub = Q()

            for value in values:
                q_sub |= get_constant_attr_q(key, value)

            q_total &= q_sub

        category_id = self.request.GET.get("category")

        if category_id:
            try:
                category_id = int(category_id)
            except (TypeError, ValueError):
                return q_total

            category = Category.objects.filter(pk=category_id).first()

            if category:
                descendant_ids = category.get_descendants(
                    include_self=True,
                ).values_list("id", flat=True)

                q_total &= Q(
                    product__category_id__in=descendant_ids,
                )

        return q_total


class CollectionListView(DetailView):
    model = CollectionList
    template_name = "catalog/collection/collection.html"


class SubCategoryListView(DetailView):
    model = Category
    template_name = "catalog/category/sub_categories.html"
    context_object_name = "category"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = self.object.get_children()
        return context


class ProductGroupListView(
    mixins.AjaxSortingResponse,
    mixins.StockContexMixin,
    ListView,
):
    model = ProductList
    template_name = "catalog/collection/product_group/products.html"
    AJAX_template_name = "catalog/collection/product_group/_products.html"
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object"] = self.object
        return context

    def get_queryset(self):
        product_groups = super().get_queryset()
        slug = self.kwargs["slug"]

        self.object = get_object_or_404(
            product_groups,
            slug=slug,
            status="active",
        )

        return self.get_stocks()

    def get_stocks(self):
        stocks = self.object.get_stocks()
        stocks = self.apply_filter(stocks)
        stocks = self.apply_sorting(stocks)

        return stocks

    def apply_filter(self, stocks):
        return stocks.filter(self.get_filter())

    def get_filter(self):
        q_total = Q()

        for key, values in self.request.GET.lists():
            if key not in CONSTANT_ATTR:
                continue

            q_sub = Q()

            for value in values:
                q_sub |= get_constant_attr_q(key, value)

            q_total &= q_sub

        return q_total


class SearchView(
    mixins.AjaxSortingResponse,
    mixins.StockContexMixin,
    ListView,
):
    model = StockRecord
    template_name = "catalog/search/products.html"
    AJAX_template_name = "catalog/search/_products.html"
    paginate_by = 20

    def get_queryset(self):
        stocks = super().get_queryset().filter(status="public")
        return self.get_stocks(stocks)

    def get_stocks(self, stocks):
        stocks = self.apply_filter(stocks)
        stocks = self.apply_sorting(stocks)
        return stocks

    def apply_filter(self, stocks):
        return stocks.filter(self.get_filter())

    def get_filter(self):
        q_total = Q()

        for key, values in self.request.GET.lists():
            if key not in CONSTANT_ATTR:
                continue

            q_sub = Q()

            for value in values:
                q_sub |= get_constant_attr_q(key, value)

            q_total &= q_sub

        return q_total

    def render_to_response(self, *args, **kwargs):
        is_search = self.request.headers.get("SEARCH", "").lower() == "true"

        if is_search:
            return self.render_json_search()

        return super().render_to_response(*args, **kwargs)

    def render_json_search(self):
        results = (
            self.object_list.annotate(
                title=F("product__title"),
                category=F("product__category__name"),
            )
            .values("title", "category")
            .distinct()[:3]
        )

        return JsonResponse(list(results), safe=False)
