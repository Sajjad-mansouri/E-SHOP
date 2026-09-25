import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from order.models import Order


class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
        ("CANCELLED", "Cancelled"),
    ]

    PAYMENT_METHOD_CHOICES = [
        ("CREDIT_CARD", "Credit Card"),
        ("PAYPAL", "PayPal"),
        ("BANK_TRANSFER", "Bank Transfer"),
        ("Test", "Test"),
    ]

    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, verbose_name=_("order")
    )
    transaction_id = models.UUIDField(
        _("Transaction ID"),
        default=uuid.uuid4,
        editable=False,
        unique=True,
        blank=True,
        null=True,
    )
    amount = models.DecimalField(_("Amount"), max_digits=10, decimal_places=2)
    currency = models.CharField(_("Currency"), max_length=3, default="USD")

    status = models.CharField(
        _("Status"), max_length=20, choices=PAYMENT_STATUS_CHOICES, default="PENDING"
    )
    payment_method = models.CharField(
        _("Payment method"),
        max_length=50,
        choices=PAYMENT_METHOD_CHOICES,
        default="Test",
    )
    gateway_response = models.JSONField(_("Gateway Response"), blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.id} for Order {self.order.id} - {self.status}"
