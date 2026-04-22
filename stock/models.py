from decimal import Decimal
from django.db import models
from django.db.models import Q, Avg, Sum
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib import admin

from comment.models import Comment


User = get_user_model()

class StockRecord(models.Model):
	STATUS_CHOICES = [
		("public", "Public"),
		("private", "Private")
	]
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
	status = models.CharField(_("status"), choices=STATUS_CHOICES, default="public", max_length=10)
	comments = GenericRelation(Comment, related_query_name="stockrecord")
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
	offer_discount = models.IntegerField(_("Offer Discount"), default=0 , validators=[MinValueValidator(0),MaxValueValidator(100)])
	rating = models.FloatField(_("rating"), default=0.0)
	sold = models.IntegerField(_("Sold"), default=0)

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
		product_discounts = self.get_offer_discount

		if not product_discounts:
			last_offer_priority = 0
			product_discounts.append((self.discount, last_offer_priority, ""))


		return product_discounts

	@property
	def get_offer_discount(self):
		product_discounts = []
		offer_apps = self.offer_apps.select_related("offer").filter(Q(offer__status="active"))
		if offer_apps:
			offer_app = offer_apps[0]
			product_discounts.append((offer_app.offer_discount, offer_app.offer.priority, offer_app.offer.name))
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
		if not self.price:
			return 0
		discount = self.get_discount

		return self.price - (self.price * (discount/100))

	@property
	def output_display_final_price(self):
		if self.price:
			return f"${self.get_final_price}"
		elif not self.price or self.quantity == 0:
			return "Out of Stock"


	@property
	def get_product_image(self):
		images = self.product.images.all()
		if images.count()>0:
			return self.product.images.all()[0].image.url
		else:
			return ""

	@property
	def get_sold_count(self):

		agg = self.stock_carts.filter(Q(cart__order__status__in=["pending", "processing", "shipped","delivered"])).aggregate(sell_count=Sum("quantity"))
		return agg["sell_count"]


	def save(self, *args, **kwargs):
		agg = self.comments.aggregate(rating_mean=Avg("rating", default=0))
		self.rating = agg["rating_mean"]
		super().save(*args, **kwargs)