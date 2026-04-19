from django.forms.models import inlineformset_factory
from django import forms
from django.forms.models import BaseInlineFormSet
from django.utils import timezone
from django.db.models import Q
from catalog.models import Product, ProductImage, ProductCategory, ProductClass, ProductAttributeValue, ProductAttribute, Category
from stock.models import StockRecord
from treebeard.forms import movenodeform_factory
from offer.models import OfferRange, Offer, OfferType, OfferApplication
from .widgets import TableCheckboxSelectMultiple, NameCheckboxSelectMultiple, OfferProductApplySelect
from coupon.models import Coupon
from order.models import Order
from comment.models import Comment

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


ProductCategoryInline = inlineformset_factory(Product, ProductCategory, form=ProductCategoryForm,fields = ["category"],extra=1, can_delete=False)

def _text_form(attr):
	return forms.CharField(widget=forms.TextInput(attrs={"class":"form-control"}), label=attr.name, required=False)

def _decimal_form(attr):
	return forms.DecimalField(widget=forms.NumberInput(attrs={"class":"form-control"}), label=attr.name, required=False)

def _integer_form(attr):
	return forms.IntegerField(widget=forms.NumberInput(attrs={"class":"form-control"}), label=attr.name, required=False)

def _boolean_form(attr):
	return forms.BooleanField(widget=forms.CheckboxInput(attrs={"class":"form-control"}), label=attr.name, required=False)

def _float_form(attr):
	return forms.FloatField(widget=forms.NumberInput(attrs={"class":"form-control"}), label=attr.name, required=False)

def _richtext_form(attr):
	return forms.CharField(widget=forms.Textarea(attrs={"class":"form-control","rows":5}), label=attr.name, required=False)

def _date_form(attr):
	return forms.DateField(widget=forms.DateInput(attrs={"class":"form-control","type":"date"}, required=False), 
							label=attr.name)

def _datetime_form(attr):

	return forms.DateTimeField(widget=forms.DateTimeInput(attrs={"class":"form-control"}, required=False), 
								label=attr.name)

def _file_form(attr):
	return forms.FileField(widget=forms.ClearableFileInput(attrs={"class":"form-control"}), label=attr.name, required=False)

def _image_form(attr):
	return forms.ImageField(widget=forms.ClearableFileInput(attrs={"class":"form-control"}), label=attr.name, required=False)


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
		fields = ["title", "upc", "short_description", "description", "product_class", "meta_title", "meta_description", "slug",]
		widgets = {
			"product_class":forms.Select(attrs={"class":"form-control"}),

			"title":forms.TextInput(attrs={"class":"form-control", "placeholder":"e.g. Sony WH‑1000XM5"}),
			"upc":forms.TextInput(attrs={"class":"form-control"}),
			"short_description":forms.TextInput(attrs={"class":"form-control", "placeholder":"e.g. Sony WH‑1000XM5"}),

			"description":forms.Textarea(attrs={"class":"form-control","rows":5}),
			"slug":forms.TextInput(attrs={"class":"form-control","placeholder":"sony-wh-1000xm5"}),
			"meta_title":forms.TextInput(attrs={"class":"form-control"}),
			"meta_description":forms.Textarea(attrs={"class":"form-control","rows":3}),


		}

	def __init__(self,product_class ,*args , **kwargs):
		super().__init__(*args, **kwargs)
		instance = kwargs.get("instance")

		if product_class:
			self.product_class = product_class
			attrs = product_class.attributes.all()
			for attr in attrs:

				initial = None
				if self.instance.id:
					try:
						attr_value = ProductAttributeValue.objects.get(product=self.instance, attribute=attr)
						initial = attr_value.get_value
					except ProductAttributeValue.DoesNotExist:
						pass

				self.fields[f"attr_{attr.name}"] = self.ATRIBUTES_FORMS[attr.type](attr)
				self.fields[f"attr_{attr.name}"].initial = initial


	def save(self, commit=True):

		product = super().save(commit=True)

		if commit:

				attrs = []
				for field_name, field_value in self.cleaned_data.items():
					if field_name.startswith('attr'):
						attr_name = field_name.split("attr_")[1]
						attr = self.product_class.attributes.get(name=attr_name)

						attr_dict = {"product":product, "attribute":attr, f"value_{attr.type}":field_value}
						if self.instance:
							ProductAttributeValue.objects.update_or_create(product=product, attribute=attr, defaults={f"value_{attr.type}":field_value})
						attrs.append(attr_dict)

				if not self.instance:
					product_attrs = [ProductAttributeValue(**attr) for attr in attrs]
					ProductAttributeValue.objects.bulk_update(product_attrs)

		return product

class ProductImageForm(forms.ModelForm):

	class Meta:
		model=ProductImage
		fields = ["image", "display_order","caption"]
		widgets = {
			"display_order":forms.HiddenInput(),
			"caption":forms.TextInput(attrs={"class":"form-control", "placeholder":"Caption (optional)"}),
			"DELETE":forms.HiddenInput()
		}
image_formset = inlineformset_factory(Product, ProductImage,fields = ["image", "display_order","caption"],form=ProductImageForm,extra=1)


class StockRecordForm(forms.ModelForm):
	def __init__(self, *args, offer_discount=None, **kwargs):
		print(kwargs)
		super().__init__(*args, **kwargs)
		print(offer_discount)
		if offer_discount:
			 self.fields['offer_discount'] = forms.FloatField(widget=forms.NumberInput(attrs={"class":"form-control"}))

	class Meta:
		model = StockRecord
		fields = ["sku", "num_in_stock", "price", "discount"]
		widgets = {
			"sku":forms.TextInput(attrs={"class":"form-control", "placeholder":"SKU"}),
			"num_in_stock":forms.NumberInput(attrs={"class":"form-control"}),
			"price":forms.NumberInput(attrs={"class":"form-control"}),
			"discount":forms.NumberInput(attrs={"class":"form-control", "placeholder":"percent"}),


		}


StockRecordInlineForm = inlineformset_factory(Product, StockRecord,fields = ["sku", "num_in_stock", "price", ],form=StockRecordForm,extra=1)



class ProductTypeForm(forms.ModelForm):
	class Meta:
		model = ProductClass
		fields = ["name",]
		widgets = {
			"name":forms.TextInput(attrs={"class":"form-control"})
		}
class ProductAttributeeForm(forms.ModelForm):

	class Meta:
		model = ProductAttribute
		fields = ["name", "type"]
		widgets = {
			"name":forms.TextInput(attrs={"class":"form-control", "placeholder":"Attribute name"}),
			"type":forms.Select(attrs={"class":"form-control"}),

		}
class CustomInlineFormSet(BaseInlineFormSet):
	def add_fields(self, form, index):
		super().add_fields(form, index)
		form.fields["DELETE"].widget = forms.HiddenInput(attrs={"class":"delete-flag"})

product_type_attr_formset = inlineformset_factory(ProductClass, ProductAttribute,fields = ["name", "type"], form=ProductAttributeeForm, formset=CustomInlineFormSet,extra=0,can_delete=True)


CategoryFormFactory = movenodeform_factory(Category)
class CategoryForm(CategoryFormFactory):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		print(self.fields)
		for field_name, field in self.fields.items():
			field.widget.attrs.update({"class":"form-control"})
		print(self.fields["product_class"].widget.attrs)




class OfferRangeForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.fields["included_products"].queryset = StockRecord.objects.filter(is_public=True)
		self.fields["excluded_products"].queryset = StockRecord.objects.filter(is_public=True)

	class Meta:
		model = OfferRange
		fields = [
				"name", "description", "is_public", 
				"includes_all_products", "included_products",
				"excluded_products", "classes",
				"included_categories", "excluded_categories"

				]

		widgets = {
				"included_products":TableCheckboxSelectMultiple(),
				"excluded_products":TableCheckboxSelectMultiple(),
				"classes":NameCheckboxSelectMultiple(),
				"included_categories":NameCheckboxSelectMultiple(),
				"excluded_categories":NameCheckboxSelectMultiple(),


		}
		

class OfferDetailForm(forms.ModelForm):
	class Meta:
		model = Offer
		fields = ["name", "description", "status", "priority"]
		widgets = {
			"name":forms.TextInput(attrs={"class":"form-control", "placeholder":"e.g. Summer sale 20%"}),
			"description":forms.Textarea(attrs={"class":"form-control", "rows":4, "placeholder":"Offer description..."}),
			"status":forms.Select(attrs={"class":"form-select"}),
			"priority":forms.NumberInput(attrs={"class":"form-control"})
		}

class OfferTypeForm(forms.ModelForm):
	class Meta:
		model = OfferType
		fields = ["offer_range", "type", "max_discount"]
		widgets = {
			"offer_range":forms.Select(attrs={"class":"form-select"}),
			"type":forms.Select(attrs={"class":"form-select"}),

			"max_discount":forms.NumberInput(attrs={"class":"form-control"})
		}

class OfferRestrictionForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields["start_datetime"].initial = timezone.now
		self.fields["end_datetime"].initial = timezone.now
		
	class Meta:
		model = Offer
		fields = ["max_discount", "start_datetime", "end_datetime"]
		widgets = {
			"max_discount":forms.NumberInput(attrs={"class":"form-control", "placeholder":"10.00"}),
			"start_datetime":forms.DateTimeInput(attrs={"class":"form-control", "type":"datetime-local"}),
			"end_datetime":forms.DateTimeInput(attrs={"class":"form-control", "type":"datetime-local"}),

		}

class CouponForm(forms.ModelForm):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for field_name, field in self.fields.items():
			field.widget.attrs.update({"class":"form-control"})
	class Meta:
		model = Coupon
		fields = ["code", "description", "valid_from", "valid_to", "discount", "active", "usage"]
		widgets = {
				"valid_from":forms.DateTimeInput(attrs={"type":"datetime-local"}),
				"valid_to":forms.DateTimeInput(attrs={"type":"datetime-local"}),

		}


class OrderStatusForm(forms.ModelForm):
	class Meta:
		model = Order
		fields = ["status"]
		widgets = {
			"status":forms.Select(attrs={"class":"status-select"})

		}

class CommentStatusForm(forms.ModelForm):
	class Meta:
		model = Comment
		fields = ["status"]


class AppliedOfferForm(forms.ModelForm):
	class Meta:
		model = OfferApplication
		fields = ["offer", "stock", "offer_discount"]
		widgets = {
		"stock":OfferProductApplySelect()
		}