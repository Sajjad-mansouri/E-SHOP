import uuid
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from address.models import Address
from cart.models import Cart
from shipping.models import Shipping
from stock.models import StockRecord

UserModel = get_user_model()


class Order(models.Model):
    STATUS_PENDING = "pending"
    STATUS_PROCESSING = "processing"
    STATUS_SHIPPED = "shipped"
    STATUS_DELIVERED = "delivered"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, _("Pending")),
        (STATUS_PROCESSING, _("Processing")),
        (STATUS_SHIPPED, _("Shipped")),
        (STATUS_DELIVERED, _("Delivered")),
        (STATUS_CANCELLED, _("Cancelled")),
    ]

    cart = models.ForeignKey(
        Cart,
        related_name="orders",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Cart"),
    )

    user = models.ForeignKey(
        UserModel,
        related_name="orders",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("User"),
    )

    shipping_address = models.ForeignKey(
        Address,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Shipping Address"),
    )

    shipping_method = models.ForeignKey(
        Shipping,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Shipping Method"),
    )

    order_number = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    # -------------------------
    # Financial snapshot
    # -------------------------

    subtotal = models.DecimalField(
        _("Subtotal"),
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    discount_amount = models.DecimalField(
        _("Discount Amount"),
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    tax_rate = models.DecimalField(
        _("Tax Rate"),
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    tax_amount = models.DecimalField(
        _("Tax Amount"),
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    shipping_amount = models.DecimalField(
        _("Shipping Amount"),
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    total_amount = models.DecimalField(
        _("Total Amount"),
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    # -------------------------
    # Coupon snapshot
    # -------------------------

    coupon_code = models.CharField(
        _("Coupon Code"),
        max_length=50,
        blank=True,
    )

    coupon_discount_percent = models.DecimalField(
        _("Coupon Discount Percent"),
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    created_at = models.DateTimeField(
        default=timezone.now,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")

    def __str__(self):
        return f"Order {self.order_number}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name="items",
        on_delete=models.CASCADE,
        verbose_name=_("Order"),
    )

    # Keep the relationship for reference, but don't depend on it
    # for historical pricing.
    stock = models.ForeignKey(
        StockRecord,
        related_name="order_items",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Stock"),
    )

    quantity = models.PositiveIntegerField(
        _("Quantity"),
    )

    # Snapshot of the price at checkout.
    unit_price = models.DecimalField(
        _("Unit Price"),
        max_digits=10,
        decimal_places=2,
    )

    # Snapshot of the line total at checkout.
    total_price = models.DecimalField(
        _("Total Price"),
        max_digits=10,
        decimal_places=2,
    )

    # These preserve what the customer actually bought even if
    # the referenced stock/product is later changed.
    product_name = models.CharField(
        _("Product Name"),
        max_length=255,
    )

    sku = models.CharField(
        _("SKU"),
        max_length=100,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        verbose_name = _("Order Item")
        verbose_name_plural = _("Order Items")
        ordering = ["id"]

    def __str__(self):
        return f"{self.quantity} × {self.product_name}"

    def calculate_total(self):
        return self.unit_price * self.quantity
