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