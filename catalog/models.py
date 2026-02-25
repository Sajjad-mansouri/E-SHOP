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