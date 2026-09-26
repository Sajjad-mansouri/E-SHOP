import zoneinfo
from datetime import datetime, timedelta
from decimal import Decimal

from django import forms as dj_forms
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import Avg, Count, Max, Prefetch, Q, Sum
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic.base import TemplateResponseMixin, TemplateView, View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView

from catalog.models import Category, Product, ProductClass
from collection.models import CollectionList, ProductList
from comment.models import Comment
from coupon.models import Coupon
from offer.models import Offer, OfferApplication, OfferRange
from order.models import Order, OrderItem
from stock.models import StockRecord

from . import forms
from .mixins import (
    AjaxQuerysetMixin,
    DeleteMixin,
    FormHandlerMixin,
    IsSellerMixin,
    StockRecordContexMixin,
    collectionMixin,
)
from .wizard_views import OfferWizardStepView

UserModel = get_user_model()


# Create your views here.
class DashboardOverView(IsSellerMixin, TemplateView):
    template_name = "dashboard/overview/overview.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        orders = self.get_orders()

        context["customers"] = self.get_customers()
        context["stock_records"] = self.get_stock_products()
        context["orders"] = orders
        context["today_orders"] = self.get_today_orders(orders)
        context["earns"] = self.get_revenue(orders)

        return context

    def get_customers(self):
        return UserModel.objects.filter(
            user_type="customer",
        )

    def get_stock_products(self):
        return StockRecord.objects.filter(
            status="public",
            num_in_stock__gt=0,
        )

    def get_orders(self):
        return Order.objects.all()

    def get_today_orders(self, orders):
        today = timezone.localdate()
        return orders.filter(
            created_at__date=today,
        )

    def get_revenue(self, orders):
        revenue_statuses = [
            "paid",
            "shipped",
            "delivered",
        ]

        revenue = orders.filter(
            status__in=revenue_statuses,
        ).aggregate(
            total=Sum("total_amount"),
        )["total"]

        return revenue or Decimal("0.00")


class ProductListView(IsSellerMixin, AjaxQuerysetMixin, ListView):
    template_name = "dashboard/catalog/product/list.html"
    model = StockRecord
    Ajax_template = "dashboard/catalog/product/_list.html"
    paginate_by = 10
    filterable = True
    searchable = True

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(product__seller=self.request.user)
            .select_related(
                "product",
                "product__category",
                "product__category__product_class",
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["category_form"] = dj_forms.modelform_factory(
            Product,
            fields=["category"],
        )

        return context

    def apply_filter(self, qs):
        status = self.request.GET.get("status")

        if status and status != "all":
            qs = qs.filter(status=status)

        return qs

    def search(self, qs):
        search = self.request.GET.get("search")

        if search:
            qs = qs.filter(
                Q(product__title__icontains=search)
                | Q(product__upc__icontains=search)
                | Q(sku__icontains=search)
            )

        return qs


class CreateUpdateProductView(
    IsSellerMixin,
    TemplateResponseMixin,
    View,
):
    template_name = "dashboard/catalog/product/create_update.html"

    def dispatch(self, request, *args, **kwargs):
        product_id = kwargs.get("pk")
        category_id = kwargs.get("category_id")

        self.product = None
        self.stock = None
        self.category = None
        self.product_class = None

        if product_id:
            self.product = get_object_or_404(
                Product.objects.select_related(
                    "category__product_class",
                ),
                pk=product_id,
                seller=request.user,
            )

            self.category = self.product.category

            if self.category:
                self.product_class = self.category.product_class

            self.stock = getattr(
                self.product,
                "stock_record",
                None,
            )

        elif category_id:
            self.category = get_object_or_404(
                Category.objects.select_related(
                    "product_class",
                ),
                pk=category_id,
            )

            self.product_class = self.category.product_class

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        product_form = forms.ProductForm(
            self.product_class,
            instance=self.product,
            prefix="product",
        )

        image_formset = forms.image_formset(
            instance=self.product,
            prefix="img",
        )

        offer_discount = bool(self.stock and self.stock.get_offer_discount)

        stock_record_form = forms.StockRecordForm(
            offer_discount=offer_discount,
            instance=self.stock,
        )

        return self.render_to_response(
            {
                "product_form": product_form,
                "img_formset": image_formset,
                "stock_record_form": stock_record_form,
                "product_class": self.product_class,
                "object": self.product,
                "category": self.category,
            }
        )

    def post(self, request, *args, **kwargs):
        product_form = forms.ProductForm(
            self.product_class,
            data=request.POST,
            instance=self.product,
            prefix="product",
        )

        image_formset = forms.image_formset(
            data=request.POST,
            files=request.FILES,
            instance=self.product,
            prefix="img",
        )

        stock_record_form = forms.StockRecordForm(
            data=request.POST,
            instance=self.stock,
        )

        if not product_form.is_valid():
            return self._render_invalid(
                product_form,
                image_formset,
                stock_record_form,
            )

        if not image_formset.is_valid():
            return self._render_invalid(
                product_form,
                image_formset,
                stock_record_form,
            )

        if not stock_record_form.is_valid():
            return self._render_invalid(
                product_form,
                image_formset,
                stock_record_form,
            )

        with transaction.atomic():
            product = product_form.save(commit=False)

            # Ownership must never come from submitted form data.
            product.seller = request.user
            product.category = self.category
            product.save()

            # Save dynamic ProductAttributeValue records now that
            # the Product has a primary key.
            product_form.save_attributes(product)

            # Required for ModelForm fields involving many-to-many
            # relationships, if any are added later.
            product_form.save_m2m()

            image_formset.instance = product
            image_formset.save()

            stock = stock_record_form.save(commit=False)
            stock.product = product
            stock.save()

        return redirect("dashboard:products")

    def _render_invalid(
        self,
        product_form,
        image_formset,
        stock_record_form,
    ):
        return self.render_to_response(
            {
                "product_form": product_form,
                "img_formset": image_formset,
                "stock_record_form": stock_record_form,
                "product_class": self.product_class,
                "object": self.product,
                "category": self.category,
            }
        )


class DeleteProductView(IsSellerMixin, DeleteMixin, DeleteView):
    template_name = "dashboard/delete_product.html"
    model = Product


class ProductTypeView(IsSellerMixin, AjaxQuerysetMixin, ListView):
    model = ProductClass
    template_name = "dashboard/catalog/product_type/list.html"
    Ajax_template = "dashboard/catalog/product_type/_list.html"
    paginate_by = 1
    filterable = False
    searchable = True

    def search(self, qs):
        search = self.request.GET.get("search")
        query = Q()
        if search:
            query = Q(name__icontains=search)

        return qs.filter(query)


class ProductTypeCreateUpdateView(IsSellerMixin, UpdateView):
    model = ProductClass
    form_class = forms.ProductTypeForm
    template_name = "dashboard/catalog/product_type/create_update.html"
    success_url = reverse_lazy("dashboard:product_type_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["attrs_formset"] = self.get_formset()
        return context

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            self.object = form.save(commit=False)
        formset = self.get_formset()

        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset)
        else:
            return self.form_invalid(form, formset)

    def get_object(self):
        product_type_pk = self.kwargs.get("pk")
        if product_type_pk:
            return get_object_or_404(ProductClass, pk=product_type_pk)
        else:
            return None

    def get_formset(self):
        formset = forms.product_type_attr_formset(**self.get_form_kwargs())

        return formset

    def form_valid(self, form, formset):
        success_url = self.get_success_url()
        self.object = form.save()
        formset.save()
        return HttpResponseRedirect(success_url)

    def form_invalid(self, form, formset):
        return self.render_to_response(
            self.get_context_data(form=form, formset=formset)
        )


class ProductTypeDeleteView(IsSellerMixin, DeleteMixin, DeleteView):
    model = ProductClass


class CategoryListView(IsSellerMixin, AjaxQuerysetMixin, ListView):
    template_name = "dashboard/catalog/category/categories.html"
    Ajax_template = "dashboard/catalog/product_type/_list.html"
    model = Category
    paginate_by = 10
    filterable = False
    searchable = True

    def search(self, qs):
        search = self.request.GET.get("search")
        query = Q()
        if search:
            query = Q(name__icontains=search)

        return qs.filter(query)


class SubCategoryView(IsSellerMixin, DetailView):
    template_name = "dashboard/catalog/category/categories.html"
    model = Category


class CategoryCreateView(IsSellerMixin, CreateView):
    template_name = "dashboard/catalog/category/create_update.html"
    model = Category
    form_class = forms.CategoryForm
    success_url = reverse_lazy("dashboard:categories")


class CategoryUpdateView(IsSellerMixin, UpdateView):
    template_name = "dashboard/catalog/category/create_update.html"
    model = Category
    form_class = forms.CategoryForm
    success_url = reverse_lazy("dashboard:categories")


class CategoryDeleteView(IsSellerMixin, DeleteMixin, DeleteView):
    template_name = "dashboard/category/category_delete.html"
    model = Category
    success_url = reverse_lazy("dashboard:categories")


class OfferRangeListView(IsSellerMixin, AjaxQuerysetMixin, ListView):
    model = OfferRange
    template_name = "dashboard/offer/range/list.html"
    Ajax_template = "dashboard/offer/range/_list.html"

    paginate_by = 1
    filterable = False
    searchable = True

    def search(self, qs):
        search = self.request.GET.get("search")
        query = Q()
        if search:
            query = Q(name__icontains=search)

        return qs.filter(query)


class OfferRangeCreateView(IsSellerMixin, CreateView):
    model = OfferRange
    template_name = "dashboard/offer/range/create_update.html"
    form_class = forms.OfferRangeForm
    success_url = reverse_lazy("dashboard:offer_range")


class OfferRangeUpdateView(IsSellerMixin, UpdateView):
    model = OfferRange
    template_name = "dashboard/offer/range/create_update.html"
    form_class = forms.OfferRangeForm
    success_url = reverse_lazy("dashboard:offer_range")
    search_template_name = "dashboard/offer/range/test.html"


class OfferRangeDeleteView(IsSellerMixin, DeleteMixin, DeleteView):
    model = OfferRange


class OfferListView(IsSellerMixin, AjaxQuerysetMixin, ListView):
    model = Offer
    template_name = "dashboard/offer/offer/list.html"
    Ajax_template = "dashboard/offer/offer/_list.html"

    paginate_by = 1
    filterable = True
    searchable = True

    def search(self, qs):
        search = self.request.GET.get("search")
        query = Q()
        if search:
            query = Q(name__icontains=search)

        return qs.filter(query)

    def apply_filter(self, qs):
        status = self.request.GET.get("status")
        query = Q()
        if status != "all" and status:
            query = Q(status=status)
        return qs.filter(query)


class CreateOfferView(IsSellerMixin, OfferWizardStepView):
    template_name = "dashboard/offer/offer/create_update.html"


class OfferStepView(IsSellerMixin, View):
    def get(self, request, *args, **kwargs):
        offer_step = kwargs.get("offer_step")
        offer_pk = kwargs.get("offer_pk")
        if offer_pk:
            offer = get_object_or_404(Offer, pk=offer_pk)
            offer_type = offer.offer_type
        else:
            offer = None
            offer_type = None

        if offer_step == 1:
            form = forms.OfferDetailForm(instance=offer)
        elif offer_step == 2:
            form = forms.OfferTypeForm(instance=offer_type)
        elif offer_step == 3:
            form = forms.OfferRestrictionForm(instance=offer)
        return render(
            request, f"dashboard/offer/offer/_step_{offer_step}.html", {"form": form}
        )


class UpdateOfferView(CreateOfferView):
    update = True


class DeleteOfferView(IsSellerMixin, DeleteMixin, DeleteView):
    template_name = "dashboard/offer/offer/delete.html"
    model = Offer
    success_url = reverse_lazy("dashboard:offer_list")


class CouponListView(IsSellerMixin, AjaxQuerysetMixin, ListView):
    model = Coupon
    template_name = "dashboard/offer/coupon/list.html"
    Ajax_template = "dashboard/offer/coupon/_list.html"

    paginate_by = 1
    filterable = True
    searchable = True

    def search(self, qs):
        search = self.request.GET.get("search")
        query = Q()
        if search:
            query = Q(code__icontains=search)

        return qs.filter(query)

    def apply_filter(self, qs):
        status = self.request.GET.get("status")
        query = Q()
        if status != "all" and status:
            query = Q(status=status)
        return qs.filter(query)


class CouponCreateView(IsSellerMixin, CreateView):
    model = Coupon
    form_class = forms.CouponForm
    success_url = reverse_lazy("dashboard:coupon_list")
    template_name = "dashboard/offer/coupon/create_update.html"

    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)


class CouponUpdateView(IsSellerMixin, UpdateView):
    model = Coupon
    form_class = forms.CouponForm
    success_url = reverse_lazy("dashboard:coupon_list")
    template_name = "dashboard/offer/coupon/create_update.html"


class CouponDeleteView(IsSellerMixin, DeleteMixin, DeleteView):
    model = Coupon
    success_url = reverse_lazy("dashboard:coupon_list")
    template_name = "dashboard/offer/coupon/delete.html"


class OrderListView(IsSellerMixin, AjaxQuerysetMixin, ListView):
    model = Order
    template_name = "dashboard/fulfilment/order/list.html"
    Ajax_template = "dashboard/fulfilment/order/_list.html"

    paginate_by = 10
    filterable = True
    searchable = True

    def get_queryset(self):
        seller_items = OrderItem.objects.filter(
            stock__product__seller=self.request.user,
        ).select_related(
            "stock__product",
        )

        return (
            super()
            .get_queryset()
            .filter(
                items__stock__product__seller=self.request.user,
            )
            .select_related(
                "user",
                "shipping_address",
                "shipping_method",
            )
            .prefetch_related(
                Prefetch(
                    "items",
                    queryset=seller_items,
                    to_attr="seller_items",
                ),
            )
            .distinct()
        )

    def search(self, qs):
        search = self.request.GET.get("search", "").strip()

        if not search:
            return qs

        return qs.filter(
            Q(order_number__icontains=search)
            | Q(
                shipping_address__full_name__icontains=search,
            )
            | Q(
                items__product_name__icontains=search,
            )
            | Q(
                items__sku__icontains=search,
            )
        ).distinct()

    def apply_filter(self, qs):
        status = self.request.GET.get("status")

        if status and status != "all":
            qs = qs.filter(status=status)

        return qs


class OrderDetailView(IsSellerMixin, UpdateView):
    model = Order
    form_class = forms.OrderStatusForm
    template_name = "dashboard/fulfilment/order/order_detail.html"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                items__stock__product__seller=self.request.user,
            )
            .distinct()
        )

    def form_valid(self, form):
        form.save()

        return JsonResponse(
            {
                "status": True,
                "message": "Order status updated successfully.",
            }
        )

    def form_invalid(self, form):
        return JsonResponse(
            {
                "status": False,
                "errors": form.errors.get_json_data(),
            },
            status=400,
        )


class OrderDeleteView(IsSellerMixin, DeleteMixin, DeleteView):
    model = Order

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                items__stock__product__seller=self.request.user,
            )
            .distinct()
        )


class FulfilmentStatistic(IsSellerMixin, TemplateView):
    template_name = "dashboard/fulfilment/statistics.html"

    def get(self, request, *args, **kwargs):
        if request.GET.get("filter") == "true":
            return self.get_statistics_response()

        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        orders = self.get_filtered_objects()
        statistics = self.get_count_by_status(orders)

        context.update(statistics)

        return context

    def get_statistics_response(self):
        orders = self.get_filtered_objects()
        statistics = self.get_count_by_status(orders)

        return JsonResponse(statistics)

    def get_filtered_objects(self):
        """
        Return only orders that contain at least one product belonging
        to the currently authenticated seller.
        """
        orders = Order.objects.filter(
            items__stock__product__seller=self.request.user,
        ).distinct()

        period = self.request.GET.get("period")
        is_range = self.request.GET.get("is_range") == "true"

        if is_range:
            filter_query = self.get_filter_by_range()
            return orders.filter(filter_query)

        if period and period != "total":
            filter_query = self.get_filter_by_period(period)

            if filter_query is not None:
                return orders.filter(filter_query)

        return orders

    def get_filter_by_period(self, period):
        """
        Return a date filter for the requested period.

        The range uses [start, end), meaning the end timestamp is
        exclusive. This avoids overlap between consecutive periods.
        """
        now = timezone.localtime()

        if period == "today":
            start = now.replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )
            end = start + timedelta(days=1)

        elif period == "week":
            start = (now - timedelta(days=now.weekday())).replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )
            end = start + timedelta(days=7)

        elif period == "month":
            start = now.replace(
                day=1,
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )

            if start.month == 12:
                end = start.replace(
                    year=start.year + 1,
                    month=1,
                )
            else:
                end = start.replace(
                    month=start.month + 1,
                )

        elif period == "year":
            start = now.replace(
                month=1,
                day=1,
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )
            end = start.replace(
                year=start.year + 1,
            )

        else:
            return None

        return Q(
            created_at__gte=start,
            created_at__lt=end,
        )

    def get_filter_by_range(self):
        """
        Build a timezone-aware date range.

        The selected end date is inclusive. For example:

        2026-09-01 → 2026-09-10

        includes all orders created on September 10.
        """
        range_start = self.request.GET.get("range_start")
        range_end = self.request.GET.get("range_end")
        timezone_name = self.request.GET.get("timezone")

        if not range_start or not range_end:
            return Q(pk__in=[])

        try:
            start_date = datetime.strptime(
                range_start,
                "%Y-%m-%d",
            ).date()

            end_date = datetime.strptime(
                range_end,
                "%Y-%m-%d",
            ).date()
        except ValueError:
            return Q(pk__in=[])

        if start_date > end_date:
            return Q(pk__in=[])

        try:
            tz = (
                zoneinfo.ZoneInfo(timezone_name)
                if timezone_name
                else timezone.get_current_timezone()
            )
        except zoneinfo.ZoneInfoNotFoundError:
            tz = timezone.get_current_timezone()

        start_naive = datetime.combine(
            start_date,
            datetime.min.time(),
        )

        # End date is inclusive, so move to the beginning of
        # the following day and use __lt.
        end_naive = datetime.combine(
            end_date + timedelta(days=1),
            datetime.min.time(),
        )

        start = timezone.make_aware(
            start_naive,
            tz,
        )

        end = timezone.make_aware(
            end_naive,
            tz,
        )

        return Q(
            created_at__gte=start,
            created_at__lt=end,
        )

    def get_count_by_status(self, orders):
        """
        Calculate all status counts with one database query.
        """
        print(
            orders,
            Order.objects.filter(items__stock__product__seller=self.request.user),
        )
        statistics = orders.aggregate(
            total=Count("pk", distinct=True),
            processing=Count(
                "pk",
                filter=Q(status=Order.STATUS_PROCESSING),
                distinct=True,
            ),
            shipped=Count(
                "pk",
                filter=Q(status=Order.STATUS_SHIPPED),
                distinct=True,
            ),
            delivered=Count(
                "pk",
                filter=Q(status=Order.STATUS_DELIVERED),
                distinct=True,
            ),
            cancelled=Count(
                "pk",
                filter=Q(status=Order.STATUS_CANCELLED),
                distinct=True,
            ),
        )

        return statistics


class CustomerListView(IsSellerMixin, ListView):
    template_name = "dashboard/customer/customers.html"
    queryset = UserModel.objects.filter(
        user_type="customer",
    )

    def dispatch(self, request, *args, **kwargs):
        self.is_ajax = request.headers.get("AJAX") == "true"
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        users = (
            super()
            .get_queryset()
            .filter(
                orders__items__stock__product__seller=self.request.user,
            )
            .filter(
                orders__status__in=[
                    "pending",
                    "processing",
                    "shipped",
                    "delivered",
                ],
            )
            .annotate(
                last_order=Max(
                    "orders__created_at",
                    filter=Q(
                        orders__items__stock__product__seller=self.request.user,
                        orders__status__in=[
                            "pending",
                            "processing",
                            "shipped",
                            "delivered",
                        ],
                    ),
                ),
                order_count=Count(
                    "orders",
                    filter=Q(
                        orders__items__stock__product__seller=self.request.user,
                        orders__status__in=[
                            "pending",
                            "processing",
                            "shipped",
                            "delivered",
                        ],
                    ),
                    distinct=True,
                ),
                total_spent=Sum(
                    "orders__total_amount",
                    filter=Q(
                        orders__items__stock__product__seller=self.request.user,
                        orders__status__in=[
                            "pending",
                            "processing",
                            "shipped",
                            "delivered",
                        ],
                    ),
                    distinct=True,
                ),
            )
            .distinct()
        )

        if self.is_ajax:
            users = self.filter_search(users)
            users = self.filter_status(users)
            users = self.sort_users(users)

        return users

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(
            "users",
            self.get_queryset(),
            "qs",
            UserModel.objects.filter(
                orders__items__stock__product__seller=self.request.user,
            ).filter(
                orders__status__in=[
                    "pending",
                    "processing",
                    "shipped",
                    "delivered",
                ],
            ),
        )
        context["object_list"] = self.get_queryset()
        return context

    def filter_search(self, users):
        search = self.request.GET.get("search", "").strip()

        if not search:
            return users

        return users.filter(
            Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
            | Q(email__icontains=search)
        )

    def filter_status(self, users):
        status = self.request.GET.get("status")

        if not status:
            return users

        return users.filter(profile__status=status)

    def sort_users(self, users):
        ordering = self.request.GET.get("ordering")

        ordering_options = {
            "date_joined",
            "-date_joined",
            "first_name",
            "-first_name",
            "total_spent",
            "-total_spent",
            "order_count",
            "-order_count",
        }

        if ordering in ordering_options:
            return users.order_by(ordering)

        return users

    def render_to_response(self, context, **response_kwargs):
        if self.is_ajax:
            self.template_name = "dashboard/customer/_customers.html"

        return super().render_to_response(
            context,
            **response_kwargs,
        )


class CustomerDetailView(IsSellerMixin, DetailView):
    template_name = "dashboard/customer/customer.html"
    queryset = UserModel.objects.filter(
        user_type="customer",
    )

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                orders__items__stock__product__seller=self.request.user,
            )
            .distinct()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        seller_orders = self.object.orders.filter(
            items__stock__product__seller=self.request.user,
        ).distinct()

        aggregate = seller_orders.aggregate(
            total_spent=Sum("total_amount"),
            last_order=Max("created_at"),
        )

        context["total_spent"] = aggregate["total_spent"]
        context["last_order"] = aggregate["last_order"]

        context["default_addresses"] = self.object.addresses.filter(
            is_default_address=True,
        )

        context["orders"] = seller_orders

        return context


class AddressListView(IsSellerMixin, DetailView):
    template_name = "dashboard/customer/addresses.html"
    queryset = UserModel.objects.filter(
        user_type="customer",
    )

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                orders__items__stock__product__seller=self.request.user,
            )
            .distinct()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["addresses"] = self.object.addresses.all()

        return context


class SalesReport(IsSellerMixin, ListView):
    template_name = "dashboard/report/sales_report.html"
    model = Order

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recent_orders = self.object_list[:10]
        product_selling_q, total_q = self.get_filtered_objects()
        top_selling, product_sold = self.get_top_selling_products(product_selling_q)
        total_revenue, total_orders, average_order = self.get_total_order_stat(total_q)
        context["recent_orders"] = recent_orders
        context["top_selling"] = top_selling
        context["total_revenue"] = total_revenue
        context["total_orders"] = total_orders
        context["average_order"] = average_order
        context["product_sold"] = product_sold

        return context

    def get_top_selling_products(self, product_selling_q):
        q = (
            Q(
                stock_carts__cart__order__status__in=[
                    "pending",
                    "processing",
                    "shipped",
                    "delivered",
                ]
            )
            & product_selling_q
        )
        top_selling = StockRecord.objects.annotate(
            sell_count=Sum("stock_carts__quantity", filter=q),
            revenue=Sum("stock_carts__final_item_price", filter=q),
        )
        top_selling = top_selling.order_by("-sell_count")
        top_selling_agg = top_selling.aggregate(product_sold=Sum("sell_count"))
        return top_selling, top_selling_agg["product_sold"]

    def get_total_order_stat(self, total_q):
        q = Q(status__in=["pending", "processing", "shipped", "delivered"]) & total_q
        total_agg = Order.objects.aggregate(total_revenue=Sum("total_cost", filter=q))
        avg_agg = Order.objects.aggregate(average_order=Avg("total_cost", filter=q))

        total_orders = Order.objects.filter(q).count()
        return total_agg["total_revenue"], total_orders, avg_agg["average_order"]

    def get_filtered_objects(self):
        period = self.request.GET.get("period")
        is_filter = self.request.GET.get("filter")
        is_range = self.request.GET.get("is_range")
        range_start = self.request.GET.get("range_start")
        range_end = self.request.GET.get("range_end")
        product_selling_q, total_q = Q(), Q()
        if is_filter == "true" and period != "total":
            product_selling_q, total_q = self.get_filter_by_period(
                period, is_range, range_start, range_end
            )

        return product_selling_q, total_q

    def get_filter_by_period(
        self, period=None, is_range=None, range_start=None, range_end=None
    ):
        if is_range:
            timezone_str = self.request.GET.get("timezone")
            tz = zoneinfo.ZoneInfo(timezone_str)
            start_naive = datetime.strptime(range_start, "%Y-%m-%d")
            end_naive = datetime.strptime(range_end, "%Y-%m-%d")

            start = timezone.make_aware(start_naive, tz)
            end = timezone.make_aware(end_naive, tz)

        product_selling_q = Q(stock_carts__cart__order__created_at__gte=start) & Q(
            stock_carts__cart__order__created_at__lte=end
        )

        total_q = Q(created_at__gte=start) & Q(created_at__lte=end)

        return product_selling_q, total_q

    def render_to_response(self, context, **response_kwargs):
        is_ajax = self.request.headers.get("AJAX")
        if is_ajax == "true":
            self.template_name = "dashboard/report/_report.html"
        return super().render_to_response(context, **response_kwargs)


class ReviewListView(IsSellerMixin, ListView):
    model = Comment
    template_name = "dashboard/review/reviews.html"
    context_object_name = "reviews"

    def dispatch(self, request, *args, **kwargs):
        self.is_ajax = self.request.headers.get("AJAX")
        return super().dispatch(request, *args, **kwargs)

    def render_to_response(self, context, **response_kwargs):
        if self.is_ajax == "true":
            self.template_name = "dashboard/review/_reviews.html"
        return super().render_to_response(context, **response_kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.is_ajax:
            reviews = self.search_reviews()
            context["reviews"] = reviews

        return context

    def search_reviews(self):
        search = self.request.GET.get("search")
        status = self.request.GET.get("status")
        rating = self.request.GET.get("rating")
        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")

        comments = self.object_list
        if not (search or status or rating or start_date or end_date):
            return comments
        if search:
            stock_ct = ContentType.objects.get_for_model(StockRecord)
            q1 = Q(content_type=stock_ct)
            q2 = Q(
                object_id__in=StockRecord.objects.filter(
                    product__title__icontains=search
                ).values_list("id", flat=True)
            )
            q3 = Q(user__username__icontains=search)
            comments = comments.filter((q1 & q2) | q3)

        if status and status != "all":
            comments = comments.filter(status=status)

        if rating and rating != "all":
            comments = comments.filter(rating=rating)

        if start_date:
            start = self.make_date_aware(start_date)
            comments = comments.filter(created__gte=start)
        if end_date:
            end = self.make_date_aware(end_date)
            comments = comments.filter(created__lte=end)

        return comments

    def make_date_aware(self, date):
        timezone_str = self.request.GET.get("timezone")
        tz = zoneinfo.ZoneInfo(timezone_str)
        naive_date = datetime.strptime(date, "%Y-%m-%d")
        date = timezone.make_aware(naive_date, tz)
        return date


class ReviewStatusUpdateView(IsSellerMixin, UpdateView):
    model = Comment
    form_class = forms.CommentStatusForm

    def form_valid(self, form):
        form.save()
        status = form.cleaned_data["status"]
        return JsonResponse({"status": True, "action": status})

    def form_invalid(self, form):
        return JsonResponse({"status": False})


class ReviewDeletView(IsSellerMixin, DeleteMixin, DeleteView):
    model = Comment


class AppliedOfferListView(IsSellerMixin, ListView):
    model = OfferApplication
    template_name = "dashboard/applied_offer/list.html"
    paginate_by = 1

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(stock__seller=self.request.user)
        qs = self.filter_by_offer_status(qs)
        qs = self.search(qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_active_offers"] = self.get_total_active_offers
        context["products_with_offer"] = self.get_product_with_offer
        context["expiring_offer_products"] = self.get_expired_offers_products

        return context

    @property
    def get_total_active_offers(self):
        return self.model.objects.filter(offer__status="active")

    @property
    def get_product_with_offer(self):
        total_active_offers = self.get_total_active_offers
        return self.calc_products_count(total_active_offers)

    def calc_products_count(self, offers):
        if offers:
            return offers.aggregate(total_product=Count("stock", distinct=True))
        else:
            return {"total_product": 0}

    @property
    def get_expired_offers_products(self):
        near_to_expire_offers = self.get_expiring_offer()
        return self.calc_products_count(near_to_expire_offers)

    def get_expiring_offer(self, hours=72):
        return self.get_total_active_offers.filter(
            offer__end_datetime__lte=timezone.now() + timedelta(hours=hours)
        )

    def filter_by_offer_status(self, qs):
        status = self.request.GET.get("offer")
        query = Q(offer__status=status)
        if status == "all" or not status:
            query = Q()
        return qs.filter(query)

    def search(self, qs):
        search = self.request.GET.get("search")

        if search:
            query = Q(offer__name__icontains=search) | Q(
                stock__product__title__icontains=search
            )
        else:
            query = Q()

        return qs.filter(query)

    def render_to_response(self, *args, **kwargs):
        if self.request.headers.get("AJAX"):
            self.template_name = "dashboard/applied_offer/_list.html"

        return super().render_to_response(*args, **kwargs)


class AppliedOfferCreateView(
    IsSellerMixin, StockRecordContexMixin, FormHandlerMixin, CreateView
):
    model = OfferApplication
    template_name = "dashboard/applied_offer/create.html"
    form_class = forms.AppliedOfferForm
    success_url = reverse_lazy("dashboard:applied_offers")


class AppliedOfferDeleteView(IsSellerMixin, DeleteMixin, DeleteView):
    model = OfferApplication


class ProductGroupListView(IsSellerMixin, collectionMixin, ListView):
    model = ProductList
    template_name = "dashboard/collection/product_group/list.html"
    paginate_by = 1
    filterable = True
    searchable = True

    def render_to_response(self, *args, **kwargs):
        if self.request.headers.get("AJAX"):
            self.template_name = "dashboard/collection/product_group/_list.html"

        return super().render_to_response(*args, **kwargs)


class ProductGroupCreateView(
    IsSellerMixin, StockRecordContexMixin, FormHandlerMixin, CreateView
):
    model = ProductList
    template_name = "dashboard/collection/product_group/create_update.html"
    form_class = forms.ProductGroupForm


class ProductGroupUpdateView(
    IsSellerMixin, StockRecordContexMixin, FormHandlerMixin, UpdateView
):
    model = ProductList
    template_name = "dashboard/collection/product_group/create_update.html"
    form_class = forms.ProductGroupForm


class ProductGroupDeleteView(IsSellerMixin, DeleteMixin, DeleteView):
    model = ProductList


class CollectionListView(IsSellerMixin, collectionMixin, ListView):
    model = CollectionList
    template_name = "dashboard/collection/collection_list/list.html"
    paginate_by = 1
    filterable = True
    searchable = True

    def render_to_response(self, *args, **kwargs):
        if self.request.headers.get("AJAX"):
            self.template_name = "dashboard/collection/collection_list/_list.html"

        return super().render_to_response(*args, **kwargs)


class CollectionListDeleteView(IsSellerMixin, DeleteMixin, DeleteView):
    model = CollectionList


class CollectionListCreateView(IsSellerMixin, FormHandlerMixin, CreateView):
    model = CollectionList
    template_name = "dashboard/collection/collection_list/create_update.html"
    form_class = forms.CollectionListForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["product_groups"] = ProductList.objects.filter(status="active")
        return context


class CollectionListUpdateView(IsSellerMixin, FormHandlerMixin, UpdateView):
    model = CollectionList
    template_name = "dashboard/collection/collection_list/create_update.html"
    form_class = forms.CollectionListForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["product_groups"] = ProductList.objects.filter(status="active")
        return context
