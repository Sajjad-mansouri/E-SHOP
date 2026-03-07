from django.forms.models import inlineformset_factory
from django import forms
from catalog.models import Product, ProductImage, ProductCategory, ProductClass, ProductAttributeValue
from stock.models import StockRecord


class ProductClassForm(forms.ModelForm):
	class Meta:
		model = Product
		fields = ["product_class"]

class ProductCategoryForm(forms.ModelForm):
	class Meta:
		model = ProductCategory
		fields = ["category"]
		widgets = {
			"category":forms.Select(attrs={"class":"form-control"})

		}


ProductCategoryInline = inlineformset_factory(Product, ProductCategory, form=ProductCategoryForm,fields = ["category"],extra=1)

def _text_form(attr):
	return forms.CharField(widget=forms.TextInput(attrs={"class":"form-control"}), label=attr.name)

def _decimal_form(attr):
	return forms.DecimalField(widget=forms.NumberInput(attrs={"class":"form-control"}), label=attr.name)

def _integer_form(attr):
	return forms.IntegerField(widget=forms.NumberInput(attrs={"class":"form-control"}), label=attr.name)

def _boolean_form(attr):
	return forms.BooleanField(widget=forms.CheckboxInput(attrs={"class":"form-control"}), label=attr.name)

def _float_form(attr):
	return forms.FloatField(widget=forms.NumberInput(attrs={"class":"form-control"}), label=attr.name)

def _richtext_form(attr):
	return forms.CharField(widget=forms.Textarea(attrs={"class":"form-control","rows":5}), label=attr.name)

def _date_form(attr):
	return forms.DateField(widget=forms.DateInput(attrs={"class":"form-control","type":"date"}), 
							label=attr.name)

def _datetime_form(attr):

	return forms.DateTimeField(widget=forms.DateTimeInput(attrs={"class":"form-control"}), 
								label=attr.name)

def _file_form(attr):
	return forms.FileField(widget=forms.ClearableFileInput(attrs={"class":"form-control"}), label=attr.name)

def _image_form(attr):
	return forms.ImageField(widget=forms.ClearableFileInput(attrs={"class":"form-control"}), label=attr.name)


class ProductForm(forms.ModelForm):

	ATRIBUTES_FORMS = {
	"text":_text_form,
	"Decimal":_decimal_form,
	"integer":_integer_form,
	"boolean":_boolean_form,
	"float":_float_form,
	"richtext":_richtext_form,
	"date":_date_form,
	"datetime":_datetime_form,
	"file":_file_form,
	"image":_image_form,
	}
	class Meta:
		model = Product
		fields = ["title", "upc", "description", "product_class", "meta_title", "meta_description", "slug",]
		widgets = {
			"product_class":forms.Select(attrs={"class":"form-control"}),

			"title":forms.TextInput(attrs={"class":"form-control", "placeholder":"e.g. Sony WH‑1000XM5"}),
			"upc":forms.TextInput(attrs={"class":"form-control"}),
			"description":forms.Textarea(attrs={"class":"form-control","rows":5}),
			"slug":forms.TextInput(attrs={"class":"form-control","placeholder":"sony-wh-1000xm5"}),
			"meta_title":forms.TextInput(attrs={"class":"form-control"}),
			"meta_description":forms.Textarea(attrs={"class":"form-control","rows":3}),


		}

	def __init__(self,product_class ,*args , **kwargs):
		super().__init__(*args, **kwargs)
		if product_class:
			self.product_class = product_class
			attrs = product_class.attributes.all()
			for attr in attrs:

				self.fields[f"attr_{attr.name}"] = self.ATRIBUTES_FORMS[attr.type](attr)

	def save(self, commit=True):

		product = super().save(commit=True)

		if commit:

				attrs = []
				for field_name, field_value in self.cleaned_data.items():
					if field_name.startswith('attr'):
						attr_name = field_name.split("attr_")[1]
						attr = self.product_class.attributes.get(name=attr_name)

						attr_dict = {"product":product, "attribute":attr, f"value_{attr.type}":field_value}
						attrs.append(attr_dict)


				product_attrs = [ProductAttributeValue(**attr) for attr in attrs]
				ProductAttributeValue.objects.bulk_create(product_attrs)
		return product

class ProductImageForm(forms.ModelForm):
	class Meta:
		model=ProductImage
		fields = ["image", "display_order","caption"]
		widgets = {
			"display_order":forms.HiddenInput(),
			"caption":forms.TextInput(attrs={"class":"form-control"})
		}
image_formset = inlineformset_factory(Product, ProductImage,fields = ["image", "display_order","caption"],form=ProductImageForm,extra=1)


class StockRecordForm(forms.ModelForm):
	class Meta:
		model = StockRecord
		fields = ["sku", "num_in_stock", "price", "is_public"]
		widgets = {
			"sku":forms.TextInput(attrs={"class":"form-control"}),
			"num_in_stock":forms.NumberInput(attrs={"class":"form-control"}),
			"price":forms.NumberInput(attrs={"class":"form-control"})

		}


StockRecordInlineForm = inlineformset_factory(Product, StockRecord,fields = ["sku", "num_in_stock", "price", "is_public"],form=StockRecordForm,extra=1)



