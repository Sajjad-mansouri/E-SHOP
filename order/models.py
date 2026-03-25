import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from stock.models import StockRecord
from cart.models import Cart
from address.models import Address

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
    order_number = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.order_number}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")



