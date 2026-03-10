from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from catalog.models import Product, ProductClass, Category

class OfferRange(models.Model):
	name = models.CharField(_("Name"), max_length=100, unique=True)
	slug = models.SlugField( _("Slug"), max_length=100, unique=True, blank=True)
	description = models.TextField(_("Description"), blank=True)
	is_public = models.BooleanField(_("Is public?"),default=True)
	includes_all_products = models.BooleanField(_("Includes all products?"), default=False)
	included_products = models.ManyToManyField(Product, 
												related_name="product_ranges",
												blank=True,
												verbose_name=_("Included Products"),
												)

	excluded_products = models.ManyToManyField(
												Product,
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
	value = models.DecimalField(
		_("Value"), decimal_places=2, max_digits=10, null=True, blank=True
	)

	class Meta:
		verbose_name = _("Offer Type")
		verbose_name_plural = _("Offer Types")

	def __str__(self):
		return f"{self.offer_range}-{self.type}:{self.value}"