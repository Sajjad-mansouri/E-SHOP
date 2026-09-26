from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Shipping(models.Model):
    SHIPPING_TYPES = [
        ("standard", _("Standard")),
        ("express", _("Express")),
    ]

    shipping_type = models.CharField(
        _("Shipping Type"),
        choices=SHIPPING_TYPES,
        max_length=10,
    )

    price = models.DecimalField(
        _("Price"),
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.00")),
        ],
    )

    free_shipping = models.BooleanField(
        _("Free Shipping"),
        default=False,
    )

    free_shipping_threshold = models.DecimalField(
        _("Free Shipping Threshold"),
        max_digits=12,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.00")),
        ],
        blank=True,
        null=True,
    )

    delivery_time = models.CharField(
        _("Delivery Time"),
        max_length=250,
    )

    created = models.DateTimeField(
        auto_now_add=True,
    )

    updated = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return self.get_shipping_type_display()

    def clean(self):
        super().clean()

        if not self.free_shipping and self.free_shipping_threshold is not None:
            raise ValidationError(
                {
                    "free_shipping_threshold": _(
                        "A free-shipping threshold can only be set "
                        "when free shipping is enabled."
                    )
                }
            )

    class Meta:
        verbose_name = _("Shipping")
        verbose_name_plural = _("Shippings")
