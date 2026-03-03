from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.conf import settings
from comment.models import Comment

User = get_user_model()

class StockRecord(models.Model):
	product = models.ForeignKey(
		"catalog.Product",
		on_delete=models.CASCADE,
		related_name="stockrecords",
		verbose_name=_("Product"),
	)

	seller = models.ForeignKey(
		User,
		on_delete=models.CASCADE,
		verbose_name=_("seller"),
		related_name="stockrecords",
	)
	comments = GenericRelation(Comment)
	sku = models.CharField(max_length=128, verbose_name=_("SKU"))
	price_currency = models.CharField(
	   max_length=12, default=settings.DEFAULT_CURRENCY, verbose_name=_("Currency")
	)
	price = models.DecimalField(
		decimal_places=2, max_digits=12, blank=True, null=True, verbose_name=_("Price"), 
	)

	num_in_stock = models.PositiveIntegerField(
		blank=True, null=True, verbose_name=_("Number in stock")
	)

	low_stock_threshold = models.PositiveIntegerField(
		blank=True, null=True, verbose_name=_("Low Stock Threshold")
	)

	# Date information
	date_created = models.DateTimeField(auto_now_add=True, verbose_name=_("Date created"))
	date_updated = models.DateTimeField(auto_now=True, db_index=True, verbose_name=_("Date updated"))


	class Meta:
		unique_together = ("seller", "sku")
		verbose_name = _("Stock record")
		verbose_name_plural = _("Stock records")

	def __str__(self):
		return f"record: seller {self.seller}, product {self.product}"
