from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from treebeard.mp_tree import MP_Node

class ProductClass(models.Model):
	"""
	used to add options for subset of products
	"""
	name = models.CharField(max_length=100, verbose_name=_("name"))
	slug = models.SlugField(max_length=100, blank=True, verbose_name=_("slug"))


	class Meta:
		ordering = ["-name"]
		verbose_name = _("Product class")
		verbose_name_plural = _("Product classes")

	def _str__(self):
		return self.name

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.name)
		super().save(*args, **kwargs)

def category_image_path(instance, image_name):
	return "images/categories/{0}/{1}".format(instance.slug,image_name)

class Category(MP_Node):
	COMPARISON_FIELDS = ("pk", "path", "depth")
	name = models.CharField(max_length=200, db_index=True, verbose_name=_("name"))
	slug = models.SlugField(max_length=200, blank=True, db_index=True, verbose_name=_("slug"))
	image = models.ImageField(upload_to=category_image_path, null=True, blank=True, verbose_name=_("image"))
	description = models.TextField(blank=True, verbose_name=_("Description"))
	long_description = models.TextField(blank=True, verbose_name=_("Long description"))

	class Meta:
		verbose_name = _("category")
		verbose_name_plural = _("categories")
	def __str__(self):
		return self.name

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.name)
		super().save(*args, **kwargs)


class Product(models.Model):

	title = models.CharField(max_length=200, verbose_name=_("title"))
	slug = models.SlugField(max_length=200, verbose_name=_("slug"))
	description = models.TextField(blank=True, verbose_name=_("Description"))
	upc = models.CharField(verbose_name=_("UPC"), help_text=_("Universal Product Code"))
	product_class = models.ForeignKey(ProductClass,
									 null=True,
									 blank=True, 
									 on_delete=models.PROTECT,
									 related_name="products",
									 verbose_name=_("product type"),
									 help_text=_("Choose what type of product this is"),
									 )
	categories = models.ManyToManyField(Category, through='ProductCategory', verbose_name=_("categories"))

	created = models.DateTimeField(auto_now_add=True, verbose_name=_("created"))
	updated = models.DateTimeField(auto_now=True, verbose_name=_("updated"))

	meta_title = models.CharField(max_length=255, blank=True, verbose_name=_('meta title'))
	meta_description = models.TextField(blank=True, verbose_name=_('meta description'))
	

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.title)
		super().save(*args, **kwargs)
		
	class Meta:
		ordering = ["-created"]
		verbose_name = _("Product")
		verbose_name_plural = _("Products")

	def __str__(self):
		return self.title


class ProductCategory(models.Model):
	category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name=_("category"))
	product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_("product"))

	class Meta:
		unique_together = ("product", "category")
		verbose_name = _("Product category")
		verbose_name_plural = _("Product categories")