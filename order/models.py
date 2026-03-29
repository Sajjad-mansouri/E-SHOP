import uuid
from decimal import Decimal
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from stock.models import StockRecord
from cart.models import Cart
from address.models import Address
from shipping.models import Shipping
from coupon.models import CouponApplication

UserModel = get_user_model()

class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    cart = models.ForeignKey(
        Cart,
        verbose_name=_("cart"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    user = models.ForeignKey(
        UserModel,
        related_name="orders",
        null=True,
        blank=True,
        verbose_name=_("User"),
        on_delete=models.SET_NULL,
    )
    shipping_address = models.ForeignKey(
        Address,
        null=True,
        blank=True,
        verbose_name=_("Shipping Address"),
        on_delete=models.SET_NULL,
    )
    shipping_method = models.ForeignKey(Shipping, on_delete=models.SET_NULL, null=True, verbose_name=_("Shipping Method"))
    order_number = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField(_("Tax Rate"), max_digits=10, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.order_number}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")

    @property
    def get_user_coupon_application(self):
        coupon_application = CouponApplication.objects.get(user=self.user, cart=self.cart)
        return coupon_application

    @property
    def get_coupon(self):
        coupon_application = self.get_user_coupon_application
        return coupon_application.coupon.code

    @property
    def get_percent_coupon_discount(self):
        coupon_application = self.get_user_coupon_application
        discount_prc = coupon_application.coupon.discount
        return Decimal(discount_prc)


    @property
    def calc_shipping_cost(self):
        if self.shipping_method.free_shipping:
            if self.cart.get_items_price > self.shipping_method.free_shipping_threshold:
                return Decimal("0.0")
            else:
                return shipping_method.price

    @property
    def calc_discount(self):
        items_price = self.calc_items_price
        discount_prc = self.get_percent_coupon_discount
        discount = (discount_prc/100)*items_price
        return discount

    @property
    def calc_tax(self):
        items_price = self.calc_items_price
        tax = items_price * Decimal((self.tax_rate/100))
        return tax

    @property
    def calc_items_price(self):
        return self.cart.get_items_price

    @property
    def calc_total_cost(self):
        items_price = self.calc_items_price
        shipping_cost = self.calc_shipping_cost
        discount = self.calc_discount
        tax = self.calc_tax
        final_cost = items_price - discount + tax + shipping_cost

        return final_cost