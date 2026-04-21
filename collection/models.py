import os
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from catalog.models import Category, ProductClass
from stock.models import StockRecord

def upload_to_class_name(instance, filename):
	"""Use the concrete model's class name as folder"""
	app_label = instance._meta.app_label
	class_name = instance.__class__.__name__.lower()
	return os.path.join(app_label, class_name, filename)

class AbstractList(models.Model):
	STATUS_CHOICE = [
		("active", "Active"),
		("suspended", "Suspended")
		]
	name = models.CharField(_("name"), max_length=250)
	slug = models.SlugField(_("slug"), max_length=250, blank=True)
	description = models.TextField(_("description"), blank=True)
	image = models.ImageField(_("image"), upload_to=upload_to_class_name, null=True, blank=True)
	status = models.CharField(choices=STATUS_CHOICE, default="active")
	categories = models.ManyToManyField(Category, verbose_name=_("categories"), blank=True)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)


	class Meta:
		abstract = True

class ProductList(AbstractList):
	stock_records = models.ManyToManyField(StockRecord, verbose_name=_("stock records"), blank=True)
	product_classes = models.ManyToManyField(ProductClass, verbose_name=_("product classes"), blank=True)

	@property
	def get_stocks(self):

		# included_products
		# excluded_products
		# classes
		# included_categories
		# excluded_categories
		included_stocks_filter = Q(id__in=self.stock_records.values("id"))
		included_categories_filter = Q(product__category__in=self.categories.values("id"))

		classes_filter = Q(product__category__product_class__in=self.product_classes.values("id"))


		_filter = (included_stocks_filter | included_categories_filter | classes_filter)
			
			
		total_stocks = StockRecord.objects.filter(_filter)

		return total_stocks

	class Meta:
		verbose_name = "Product List"
		verbose_name_plural = "Product Lists"



class CollectionList(AbstractList):
	product_lists = models.ManyToManyField(ProductList, verbose_name=_("product lists"), blank=True)

	class Meta:
		verbose_name = "Collection"
		verbose_name_plural = "Collections"