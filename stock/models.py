from decimal import Decimal
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib import admin

from comment.models import Comment
from offer.models import OfferRange, OfferType, Offer

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
	is_public = models.BooleanField(default=True)
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
	discount = models.IntegerField(_("discount"), default=0 , validators=[MinValueValidator(0),MaxValueValidator(100)])


	# Date information
	date_created = models.DateTimeField(auto_now_add=True, verbose_name=_("Date created"))
	date_updated = models.DateTimeField(auto_now=True, db_index=True, verbose_name=_("Date updated"))
	

	class Meta:
		unique_together = ("seller", "sku")
		verbose_name = _("Stock record")
		verbose_name_plural = _("Stock records")

	def __str__(self):
		return f"record: seller {self.seller}, product {self.product}"


	@property
	def get_product_discounts(self):

		offers = Offer.objects.filter(Q(status="open"))
		product_discounts = []
		for offer in offers:
			product = offer.offer_type.offer_range.get_products.filter(id=self.product.id).exists()
			product_discounts.append((offer.offer_type.value, offer.priority, offer.name))


		if not product_discounts:
			last_offer_priority = 0
		else:
			last_offer_priority = product_discounts[-1][1]+1

		product_discounts.sort(key=lambda x:x[1])
		product_discounts.append((self.discount, last_offer_priority, "personal"))
		return product_discounts

	@property
	@admin.display(description="discount(%)")
	def get_discount(self):
		product_discounts = self.get_product_discounts
		return Decimal(product_discounts[0][0])

	@property
	def has_dicounted(self):
		if self.get_discount > 0:
			return True
		else:
			return False

	@property
	@admin.display(description="discount type")
	def get_type_of_discount(self):
		product_discounts = self.get_product_discounts

		return product_discounts[0][2]

	@property
	@admin.display(description="price after discount")
	def get_final_price(self):
		discount = self.get_discount

		return self.price - (self.price * (discount/100))

	@property
	def get_product_image(self):
		images = self.product.images.all()
		if images.count()>0:
			return self.product.images.all()[0].image.url
		else:
			return ""