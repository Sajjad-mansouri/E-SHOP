from django.db import models
from django.utils.translation import gettext_lazy as _


class Shipping(models.Model):
    SHIPPING_TYPES = [("Standard", "standard"), ("Express", "express")]

    shipping_type = models.CharField(
        _("Shipping Type"), choices=SHIPPING_TYPES, max_length=10
    )
    price = models.DecimalField(_("price"), max_digits=10, decimal_places=2)
    free_shipping = models.BooleanField(_("Free Shipping"), default=False)
    free_shipping_threshold = models.DecimalField(
        _("Free Shipping"), decimal_places=2, max_digits=12, blank=True, null=True
    )
    delivery_time = models.CharField(_("Delivery time"), max_length=250)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.shipping_type

    class Meta:
        verbose_name = _("Shipping")
        verbose_name_plural = _("Shippings")
