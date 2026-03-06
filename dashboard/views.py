from django.shortcuts import render,redirect
from django.views.generic.list import ListView
from django.views.generic.base import View, TemplateResponseMixin
from .forms import image_formset, ProductForm, ProductCategoryInline, StockRecordInlineForm
from stock.models import StockRecord
from catalog.models import Product

# Create your views here.
def dashboard(request):
	context = {}
	return render(request, "dashboard/main.html",context)


class ProductListView(ListView):
	template_name = "dashboard/product_list.html"
	model = StockRecord

class CreateProductView(TemplateResponseMixin, View):
	template_name = "dashboard/create_update_product.html"

	def get(self, request, *args, **kwargs):

		img_formset = image_formset(prefix="img")
		product_form = ProductForm(prefix="product")
		product_category_form = ProductCategoryInline(prefix="category")
		stock_record_inline = StockRecordInlineForm(prefix="stock")
		return self.render_to_response({
			'img_formset':img_formset, 
			'product_form':product_form, 
			'product_category_form':product_category_form,
			'stock_record_inline':stock_record_inline
			})

	def post(self, request, *args, **kwargs):
		product = Product.objects.first()
		img_formset = image_formset(data=request.POST,files=request.FILES,prefix="img")
		product_form = ProductForm(data=request.POST, prefix="product")
		product_category_form = ProductCategoryInline(data=request.POST, prefix="category")
		stock_record_inline = StockRecordInlineForm(data=request.POST, prefix="stock")

		if img_formset.is_valid() and product_form.is_valid() and product_category_form.is_valid() and stock_record_inline.is_valid():
			
			product = product_form.save()
			images = img_formset.save(commit=False)
			for image in images:
				image.product = product
				image.save()
			stocks = stock_record_inline.save(commit=False)
			for stock in stocks:
				stock.product = product
				stock.seller = request.user
				stock.save()

			product_categories = product_category_form.save(commit=False)
			for product_category in product_categories:
				product_category.product = product
				product_category.save()

		else:
			return self.render_to_response({
				'img_formset':img_formset, 
				'product_form':product_form,
				'product_category_form':product_category_form,
				'stock_record_inline':stock_record_inline
				})

		return redirect('products')
