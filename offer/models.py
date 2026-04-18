from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from catalog.models import Product, ProductClass, Category
from stock.models import StockRecord


class OfferRange(models.Model):
	name = models.CharField(_("Name"), max_length=100, unique=True)
	slug = models.SlugField( _("Slug"), max_length=100, unique=True, blank=True)
	description = models.TextField(_("Description"), blank=True)
	is_public = models.BooleanField(_("Is public?"),default=True)
	includes_all_products = models.BooleanField(_("Includes all products?"), default=False)
	included_products = models.ManyToManyField(StockRecord, 
												related_name="product_ranges",
												blank=True,
												verbose_name=_("Included Products"),
												)

	excluded_products = models.ManyToManyField(
												StockRecord,
												related_name="exclude_product_ranges",
												blank=True,
												verbose_name=_("Excluded Products"),
												)

	classes = models.ManyToManyField(
									ProductClass,
									related_name="class_ranges",
									blank=True,
									verbose_name=_("Product Types"),
									)


	included_categories = models.ManyToManyField(
		Category,
		related_name="category_ranges",
		blank=True,
		verbose_name=_("Included Categories"),
	)
	excluded_categories = models.ManyToManyField(
		Category,
		related_name="exclude_category_ranges",
		blank=True,
		verbose_name=_("Excluded Categories"),
	)

	created = models.DateTimeField(_("Date Created"), auto_now_add=True)
	updated = models.DateTimeField(_("Date Updated"), auto_now=True)


	class Meta:
		ordering = ["name"]
		verbose_name = _("Range")
		verbose_name_plural = _("Ranges")

	def __str__(self):
		return self.name


	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.name)
		super().save(*args, **kwargs)

	@property
	def get_products(self):

		# included_products
		# excluded_products
		# classes
		# included_categories
		# excluded_categories
		included_products_filter = Q(id__in=self.included_products.values("id"))
		excluded_products_filter = ~Q(id__in=self.excluded_products.values("id"))
		included_categories_filter = Q(product__categories__in=self.included_categories.values("id"))
		excluded_categories_filter = ~Q(product__categories__in=self.excluded_categories.values("id"))
		classes_filter = Q(product__product_class__in=self.classes.values("id"))
		public_filter = Q(is_public=True) 
		if self.includes_all_products:
			_filter = (
				excluded_products_filter & excluded_categories_filter & public_filter
				)
		else:

			_filter = (
				(included_products_filter | included_categories_filter | classes_filter)
				& excluded_products_filter & excluded_categories_filter & public_filter
				)
		offer_products = StockRecord.objects.filter(_filter)

		return offer_products

	@property
	def product_count(self):
		return self.get_products.count()


class OfferType(models.Model):
	offer_range = models.ForeignKey(
		OfferRange,
		blank=True,
		null=True,
		on_delete=models.CASCADE,
		verbose_name=_("Offer Range"),
	)

	TYPE_CHOICES = [
		("Percentage", _("Discount is a percentage off of the product's value")),

		("Shipping percentage", _("Discount is a percentage off of the shipping cost")),
		("Shipping fixed price", _("Get shipping for a fixed price"))
	]
	type = models.CharField(_("Offer Type"), max_length=100, choices=TYPE_CHOICES, blank=True)
	max_discount = models.IntegerField(_("Max Discount"), default=0 , validators=[MinValueValidator(0),MaxValueValidator(100)])

	class Meta:
		verbose_name = _("Offer Type")
		verbose_name_plural = _("Offer Types")

	def __str__(self):
		return f"{self.offer_range}-{self.type}:{self.max_discount}"

class Offer(models.Model):

	name = models.CharField(
		_("Name"),
		max_length=100,
		unique=True,
	)
	slug = models.SlugField(
		_("Slug"), max_length=100, unique=True, blank=True 
	)
	desc_header = models.CharField(
		_("Description Header"),
		max_length=100,
		blank=True
	)
	description = models.TextField(
		_("Description"),
		blank=True,
	)

	image = models.ImageField(_("Image"), upload_to="offer/", blank=True, null=True)
	OFFER_STATUS = [
		("open", "open"),
		("Suspended", "Suspended"),

	]
	status = models.CharField(_("Status"), max_length=50, choices=OFFER_STATUS, default="open")

	offer_type = models.ForeignKey(
		OfferType,
		on_delete=models.CASCADE,
		related_name="offers",
		verbose_name=_("Offer Type"),
	)

	priority = models.IntegerField(
		_("Priority"),
		default=0,
		db_index=True,
		help_text=_("The highest priority offers are applied first"),
	)

	max_discount = models.DecimalField(
		_("Max discount"),
		decimal_places=2,
		max_digits=10,
		null=True,
		blank=True,
		help_text=_(
			"When an offer has given more discount to orders "
			"than this threshold, then the offer becomes "
			"unavailable"
		),
	)

	start_datetime = models.DateTimeField(
		_("Start date"),
		blank=True,
		null=True,
		help_text=_(
			"Offers are active from the start date. "
			"Leave this empty if the offer has no start date."
		),
	)
	end_datetime = models.DateTimeField(
		_("End date"),
		blank=True,
		null=True,
		help_text=_(
			"Offers are active until the end date. "
			"Leave this empty if the offer has no expiry date."
		),
	)

	created = models.DateTimeField(_("Date Created"), auto_now_add=True)
	updated = models.DateTimeField(_("Date Updated"), auto_now=True)

	class Meta:
		ordering = ["-priority", "pk"]
		verbose_name = _("offer")
		verbose_name_plural = _("offers")

	def __str__(self):
		return self.name


	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.name)
		super().save(*args, **kwargs)

	@property
	def is_valid(self):
		now = timezone.now()
		return self.start_datetime<=now<=self.end_datetime

	@property
	def get_expire(self):
		now = timezone.now()
		return self.end_datetime - now

	@property
	def get_offer_products(self):
		return self.offer_type.offer_range.get_products

class OfferApplication(models.Model):
	offer = models.ForeignKey(Offer, on_delete=models.CASCADE, verbose_name=_("offer"))
	stock = models.ForeignKey(StockRecord, on_delete=models.CASCADE, related_name="offer_apps", verbose_name=_("Stock Record"))
	offer_discount = models.IntegerField(_("Offer Discount"), default=0 , validators=[MinValueValidator(0),MaxValueValidator(100)])
	is_accepted = models.BooleanField(_("Is Accepted"), default=False)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

