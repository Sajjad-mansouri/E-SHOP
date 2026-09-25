from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from stock.models import StockRecord

UserModel = get_user_model()


# Create your models here.
class Cart(models.Model):
    user = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="carts",
        verbose_name=_("user"),
    )
    submited = models.BooleanField(_("submited"), default=False)
    date_created = models.DateTimeField(_("Date created"), auto_now_add=True)
    date_merged = models.DateTimeField(_("Date merged"), null=True, blank=True)
    date_submitted = models.DateTimeField(_("Date submitted"), null=True, blank=True)

    def __str__(self):
        return f"Cart for {self.user or 'Anonymous'}"

    class Meta:
        verbose_name = _("Cart")
        verbose_name_plural = _("Carts")

    @property
    @admin.display(description="Total Items price")
    def get_items_price(self):
        total = 0
        for item in self.items.all():
            total += item.get_item_price
        return total


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("cart"),
    )
    stock = models.ForeignKey(
        StockRecord,
        on_delete=models.CASCADE,
        related_name="stock_carts",
        verbose_name=_("stock"),
    )

    quantity = models.PositiveIntegerField(_("Quantity"), default=1)

    created = models.DateTimeField(_("Date Created"), auto_now_add=True, db_index=True)
    updated = models.DateTimeField(_("Date Updated"), auto_now=True, db_index=True)
    final_item_price = models.DecimalField(
        _("Item Price"), max_digits=10, decimal_places=2, default=0.0
    )

    def __str__(self):
        return f"{self.quantity} X {self.stock}"

    class Meta:
        verbose_name = _("Cart Item")
        verbose_name_plural = _("Cart Items")

    @property
    @admin.display(description="Item price")
    def get_item_price(self):
        stock_final_price = self.stock.get_final_price
        return stock_final_price * self.quantity

    def save(self, *args, **kwargs):
        self.final_item_price = self.get_item_price
        super().save(*args, **kwargs)
