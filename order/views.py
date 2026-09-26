from django.http import JsonResponse
from django.views.generic.edit import CreateView

from cart.models import Cart
from coupon.models import CouponApplication
from shipping.models import Shipping

from .forms import OrderForm
from .models import Order
from .services import OrderCheckoutService


class OrderCreateView(CreateView):
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
            context["cart"] = None
            context["items"] = []
            context["coupon_application"] = None
            context["final_price"] = 0
            context["discount"] = 0
            return context

        context["cart"] = cart
        context["items"] = cart.items.select_related("stock")

        coupon_application = self.get_user_application_coupon(cart)

        context["coupon_application"] = coupon_application

        subtotal = cart.get_items_price

        if coupon_application:
            discount_percent = coupon_application.coupon.discount
            discount = subtotal * discount_percent / 100
        else:
            discount = 0

        context["discount"] = discount
        context["final_price"] = subtotal - discount

        return context

    def form_valid(self, form):
        cart = self.get_user_cart()

        coupon_application = self.get_user_application_coupon(cart)

        order = OrderCheckoutService.create_order(
            user=self.request.user,
            cart=cart,
            shipping_address=form.cleaned_data["shipping_address"],
            shipping_method=form.cleaned_data["shipping_method"],
            coupon_application=coupon_application,
        )

        return JsonResponse(
            {
                "status": True,
                "order_number": str(order.order_number),
            }
        )

    def get_user_cart(self):
        return Cart.objects.get(
            user=self.request.user,
            submited=False,
        )

    def get_user_application_coupon(self, cart):
        try:
            return CouponApplication.objects.get(
                user=self.request.user,
                cart=cart,
            )
        except CouponApplication.DoesNotExist:
            return None

    def form_invalid(self, form):
        return JsonResponse(
            {
                "status": False,
                "errors": form.errors,
            },
            status=400,
        )
