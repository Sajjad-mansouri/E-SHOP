from django.forms.models import inlineformset_factory
from django import forms
from catalog.models import Product, ProductImage, ProductCategory
from stock.models import StockRecord


class ProductCategoryForm(forms.ModelForm):
	class Meta:
		model = ProductCategory
		fields = ["category"]
		widgets = {
			"category":forms.Select(attrs={"class":"form-control"})

		}


ProductCategoryInline = inlineformset_factory(Product, ProductCategory, form=ProductCategoryForm,fields = ["category"],extra=1)

class ProductForm(forms.ModelForm):
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

class ProductImageForm(forms.ModelForm):
	class Meta:
		model=ProductImage
		fields = ['image', 'display_order','caption']
		widgets = {
			"display_order":forms.HiddenInput(),
			"caption":forms.TextInput(attrs={"class":"form-control"})
		}
image_formset = inlineformset_factory(Product, ProductImage,fields = ['image', 'display_order','caption'],form=ProductImageForm,extra=1)


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