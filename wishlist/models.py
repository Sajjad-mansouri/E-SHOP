from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import UniqueConstraint
from django.utils.translation import gettext_lazy as _

from stock.models import StockRecord

UserModel = get_user_model()


# Create your models here.
class WishList(models.Model):
    user = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name="wishlists",
        verbose_name=_("user"),
    )
    stock_record = models.ForeignKey(
        StockRecord, on_delete=models.CASCADE, verbose_name=_("Stock Record")
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} add {self.stock_record} to wishlist"

    class Meta:
        verbose_name = _("Wishlist")
        verbose_name_plural = _("Wishlists")

        constraints = [
            UniqueConstraint(
                "user",
                "stock_record",
                name="user_stock_unique",
            ),
        ]
