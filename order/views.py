from decimal import Decimal

from django.http import JsonResponse
from django.views.generic.edit import CreateView

from cart.models import Cart
from coupon.models import CouponApplication
from shipping.models import Shipping

from .forms import OrderForm
from .models import Order


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
            context["cart"] = cart
            context["items"] = cart.items.all()
            coupon_application = self.get_user_application_coupon(cart)
        except Cart.DoesNotExist:
            context["cart"] = []
            context["items"] = []
            coupon_application = None

        context["coupon_application"] = coupon_application
        discount_prc = coupon_application.coupon.discount
        pre_coupon_discount_price = cart.get_items_price
        discount = Decimal(discount_prc / 100) * pre_coupon_discount_price

        final_price = pre_coupon_discount_price - discount
        print(final_price)
        context["final_price"] = final_price
        context["discount"] = discount

        return context

    def form_valid(self, form):
        cart = self.get_user_cart()

        Order.objects.filter(
            user=self.request.user, cart=cart, status="pending"
        ).delete()

        order = form.save(commit=False)
        order.user = self.request.user
        cost = self.calc_cost(form, cart)
        order.total_amount = cost
        order.cart = cart
        order.save()
        return JsonResponse({"status": True})

    def get_user_cart(self):
        cart = Cart.objects.get(user=self.request.user, submited=False)
        return cart

    def get_user_application_coupon(self, cart):
        coupon_application = CouponApplication.objects.get(
            user=self.request.user, cart=cart
        )
        return coupon_application

    def calc_cost(self, form, cart):
        tax = 0
        coupon_application = self.get_user_application_coupon(cart)

        discount_prc = coupon_application.coupon.discount
        pre_coupon_discount_price = cart.get_items_price
        shipping_cost = self.get_shipping_cost(form, pre_coupon_discount_price)
        discount = Decimal(discount_prc / 100) * pre_coupon_discount_price

        final_cost = pre_coupon_discount_price - discount + tax + shipping_cost
        return final_cost

    def get_shipping_cost(self, form, pre_coupon_discount_price):
        shipping = form.cleaned_data["shipping_method"]

        if shipping.free_shipping:
            if pre_coupon_discount_price > shipping.free_shipping_threshold:
                return 0

        return shipping.price

    def form_invalid(self, form):
        print(form.errors)
