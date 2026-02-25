from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify

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