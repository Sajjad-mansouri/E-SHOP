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

	def __str__(self):
		return self.name

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.name)
		super().save(*args, **kwargs)

	@property
	def has_attributes(self):
		return self.attributes.exists()
		
def category_image_path(instance, image_name):
	return "images/categories/{0}/{1}".format(instance.slug,image_name)

class Category(MP_Node):

	name = models.CharField(max_length=200, db_index=True, verbose_name=_("name"))
	slug = models.SlugField(max_length=200, blank=True, db_index=True, verbose_name=_("slug"))
	image = models.ImageField(upload_to=category_image_path, null=True, blank=True, verbose_name=_("image"))
	description = models.TextField(blank=True, verbose_name=_("Description"))
	long_description = models.TextField(blank=True, verbose_name=_("Long description"))

	class Meta:
		verbose_name = _("category")
		verbose_name_plural = _("categories")
	def __str__(self):

		return self.get_name

	@property
	def get_name(self):
		names = [category.name for category in self.get_ancestor_plus_self()]
		return " > ".join(names)

	def get_ancestor_plus_self(self):
		
		if self.is_root():
			return [self]

		return list(self.get_ancestors()) + [self]
	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.name)
		super().save(*args, **kwargs)



class Product(models.Model):

	title = models.CharField(max_length=200, verbose_name=_("title"))
	slug = models.SlugField(max_length=200, blank=True, verbose_name=_("slug"))
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
	attributes = models.ManyToManyField("ProductAttribute", through="ProductAttributeValue", verbose_name=_("attributes"))

	created = models.DateTimeField(auto_now_add=True, verbose_name=_("created"))
	updated = models.DateTimeField(auto_now=True, verbose_name=_("updated"))

	meta_title = models.CharField(max_length=255, blank=True, verbose_name=_('meta title'))
	meta_description = models.TextField(blank=True, verbose_name=_('meta description'))
	view_count = models.PositiveIntegerField(default=0)
	
	is_public = models.BooleanField(default=True)

	
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

	def __str__(self):
		return f"{self.category}-{self.product}"

class ProductAttribute(models.Model):

	product_class = models.ForeignKey(
									ProductClass,
									on_delete=models.CASCADE,
									null=True,
									blank=True,
									related_name="attributes",
									verbose_name=_("product type")
								)
	name = models.CharField(max_length=200, verbose_name=_("name"))

	# Attribute types
	Decimal = "Decimal"
	TEXT = "text"
	INTEGER = "integer"
	BOOLEAN = "boolean"
	FLOAT = "float"
	RICHTEXT = "richtext"
	DATE = "date"
	DATETIME = "datetime"
	FILE = "file"
	IMAGE = "image"

	TYPE_CHOICES = (
		(TEXT, _("Text")),
		(Decimal, _("Decimal")),
		(INTEGER, _("Integer")),
		(BOOLEAN, _("True / False")),
		(FLOAT, _("Float")),
		(RICHTEXT, _("Rich Text")),
		(DATE, _("Date")),
		(DATETIME, _("Datetime")),
		(FILE, _("File")),
		(IMAGE, _("Image")),
	)

	type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=TYPE_CHOICES[0][0],verbose_name=_("type"))

	class Meta:
		verbose_name = _("Product attribute")
		verbose_name_plural = _("Product attributes")

	def __str__(self):
		return self.name

def attribute_file_path(instance, filename):
	return "files/attribute/product_{0}/attr_{1}/{2}".format(instance.product.title, instance.attribute.name,filename)

def attribute_image_path(instance, image_name):
	return "images/attribute/product_{0}/attr_{1}/{2}".format(instance.product.title, instance.attribute.name,image_name)

class ProductAttributeValue(models.Model):

	product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_attributes",verbose_name=_("product"))
	attribute = models.ForeignKey(ProductAttribute, on_delete=models.CASCADE, related_name="attribute_values", verbose_name=_('attribute'))
	value_text = models.CharField(max_length=200, blank=True, verbose_name=_("Text"))
	value_decimal = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2, verbose_name=_("Decimal"))
	value_integer = models.IntegerField(blank=True, null=True, verbose_name=_("Integer"))
	value_boolean = models.BooleanField(blank=True, null=True, verbose_name=_("Boolean"))
	value_float = models.FloatField(blank=True, null=True, verbose_name=_("Float"))
	value_richtext = models.TextField(blank=True, verbose_name=_("Rich text"))
	value_date = models.DateField(null=True, blank=True, verbose_name=_("Datetime"))
	value_datetime = models.DateTimeField(null=True, blank=True, verbose_name=_("Datetime"))
	value_file = models.FileField(null=True, blank=True, upload_to=attribute_file_path)
	value_image = models.ImageField(null=True, blank=True, upload_to=attribute_image_path)

	class Meta:
		verbose_name = _("Product attribute value")
		verbose_name_plural = _("Product attribute values")


	def __str__(self):

		return f"{self.attribute}:{self.get_value}"

	@property
	def get_value(self):
		ATTRIBUTE_TYPE = {
		"text":self.value_text,
		"Decimal":self.value_decimal,
		"integer":self.value_integer,
		"boolean":self.value_boolean,
		"float":self.value_float,
		"richtext":self.value_richtext,
		"date":self.value_date,
		"datetime":self.value_datetime,
		"file":self.value_file,
		"image":self.value_image

		}
		return ATTRIBUTE_TYPE[self.attribute.type]

def product_image_path(instance, image_name):
	return "images/product/{0}/{1}".format(instance.product.title,image_name)


class ProductImage(models.Model):

	product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images", verbose_name=_("product"))
	image = models.ImageField(upload_to=product_image_path, verbose_name=_("image"))
	display_order = models.PositiveIntegerField(default=0, db_index=True, verbose_name=_("display order"))
	caption = models.CharField(max_length=200, blank=True, verbose_name=_("caption"))
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["display_order"]
		verbose_name = _("Product image")
		verbose_name_plural = _("Product images")
	def __str__(self):
		return f'{self.product} image'