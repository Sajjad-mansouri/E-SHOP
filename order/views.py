from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.generic.edit import CreateView

from cart.models import Cart
from coupon.models import CouponApplication
from shipping.models import Shipping

from .forms import OrderForm
from .models import Order
from .services import OrderService


class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = "order/create_order.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["addresses"] = self.request.user.addresses.all()
        context["shipping_methods"] = Shipping.objects.all()

        try:
            cart = self.get_user_cart()
        except Cart.DoesNotExist:
            context.update(
                {
                    "cart": None,
                    "items": [],
                    "coupon_application": None,
                    "final_price": Decimal("0.00"),
                    "discount": Decimal("0.00"),
                }
            )
            return context

        items = cart.items.select_related(
            "stock",
            "stock__product",
        )

        context["cart"] = cart
        context["items"] = items

        coupon_application = self.get_user_application_coupon(cart)
        context["coupon_application"] = coupon_application

        subtotal = Decimal("0.00")

        for item in items:
            subtotal += item.stock.get_final_price * item.quantity

        if coupon_application:
            discount_percent = coupon_application.coupon.discount
            discount = (subtotal * discount_percent / Decimal("100")).quantize(
                Decimal("0.01")
            )
        else:
            discount = Decimal("0.00")

        context["discount"] = discount
        context["final_price"] = subtotal - discount

        return context

    def form_valid(self, form):
        try:
            cart = self.get_user_cart()
        except Cart.DoesNotExist:
            return JsonResponse(
                {
                    "status": False,
                    "error": "Your cart is empty.",
                },
                status=400,
            )

        coupon_application = self.get_user_application_coupon(cart)

        try:
            order = OrderService.create_order(
                user=self.request.user,
                cart=cart,
                shipping_address=form.cleaned_data["shipping_address"],
                shipping_method=form.cleaned_data["shipping_method"],
                coupon_application=coupon_application,
            )
        except ValueError as exc:
            return JsonResponse(
                {
                    "status": False,
                    "error": str(exc),
                },
                status=400,
            )

        return JsonResponse(
            {
                "status": True,
                "order_number": str(order.order_number),
                "order_id": str(order.id),
            }
        )

    def get_user_cart(self):
        return Cart.objects.get(
            user=self.request.user,
            submited=False,
        )

    def get_user_application_coupon(self, cart):
        return (
            CouponApplication.objects.filter(
                user=self.request.user,
                cart=cart,
            )
            .select_related("coupon")
            .first()
        )

    def form_invalid(self, form):
        return JsonResponse(
            {
                "status": False,
                "errors": form.errors,
            },
            status=400,
        )
