from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from stock.models import StockRecord

UserModel = get_user_model()

# Create your models here.
class Cart(models.Model):
	user = models.ForeignKey(UserModel, on_delete=models.CASCADE, null=True, blank=True, related_name="carts", verbose_name=_("user"))
	submited = models.BooleanField(_("submited"), default=False)
	date_created = models.DateTimeField(_("Date created"), auto_now_add=True)
	date_merged = models.DateTimeField(_("Date merged"), null=True, blank=True)
	date_submitted = models.DateTimeField(_("Date submitted"), null=True, blank=True)

	def __str__(self):
		return f"Cart for {self.user or 'Anonymous'}"

	class Meta:
		verbose_name = _("Cart")
		verbose_name_plural = _("Carts")


class CartItem(models.Model):
	cart = models.ForeignKey(
		Cart,
		on_delete=models.CASCADE,
		related_name="items",
		verbose_name=_("cart"),
	)
	stock = models.ForeignKey(
		StockRecord, on_delete=models.CASCADE, related_name="stock_carts", verbose_name=_("stock")
	)

	quantity = models.PositiveIntegerField(_("Quantity"), default=1)

	created = models.DateTimeField(_("Date Created"), auto_now_add=True, db_index=True)
	updated = models.DateTimeField(_("Date Updated"), auto_now=True, db_index=True)

	def __str__(self):
		return f"{self.quantity} X {self.stock}"

	class Meta:
		verbose_name = _("Cart Item")
		verbose_name_plural = _("Cart Items")
