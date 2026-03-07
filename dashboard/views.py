from django.shortcuts import render,redirect,get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.base import View, TemplateResponseMixin
from django.forms.models import inlineformset_factory
from .forms import image_formset, ProductForm, ProductCategoryInline, StockRecordInlineForm, ProductClassForm
from stock.models import StockRecord
from catalog.models import Product, ProductClass, ProductAttribute, ProductAttributeValue


# Create your views here.
def dashboard(request):
	context = {}
	return render(request, "dashboard/main.html",context)


class ProductListView(ListView):
	template_name = "dashboard/product_list.html"
	model = StockRecord

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		product_class_form = ProductClassForm()
		context['product_class_form'] = product_class_form
		return context

class CreateUpdateProductView(TemplateResponseMixin, View):
	template_name = "dashboard/create_update_product.html"

	def dispatch(self, request, *args, **kwargs):
		product_class_id = request.GET.get('product_class')
		product_id = kwargs.get('id')
		if product_id:
			self.product = get_object_or_404(Product, id=product_id)
			self.product_class = self.product.product_class
			print('product class',self.product_class)
		if product_class_id:
			self.product_class = get_object_or_404(ProductClass, id=product_class_id)
		elif not product_id:
			self.product_class = None
		return super().dispatch(request, *args, **kwargs)

	def get(self, request, *args, **kwargs):

		img_formset = image_formset(instance=self.product, prefix="img")
		product_form = ProductForm(self.product_class , instance=self.product,prefix="product")

		product_category_form = ProductCategoryInline(instance=self.product, prefix="category")
		stock_record_inline = StockRecordInlineForm(instance=self.product, prefix="stock")
		print('self.product_class', self.product_class)
		return self.render_to_response({
			"img_formset":img_formset, 
			"product_form":product_form, 
			"product_category_form":product_category_form,
			"stock_record_inline":stock_record_inline,
			"product_class":self.product_class


			})

	def post(self, request, *args, **kwargs):

		product_form = ProductForm(self.product_class, instance=self.product, data=request.POST, prefix="product")
		if product_form.is_valid():
			self.object = product_form.save()


		img_formset = image_formset(data=request.POST,files=request.FILES,instance=self.object, prefix="img")
		product_category_form = ProductCategoryInline(data=request.POST,instance=self.object,  prefix="category")
		stock_record_inline = StockRecordInlineForm(data=request.POST,instance=self.object,  prefix="stock")

		if img_formset.is_valid() and product_category_form.is_valid() and stock_record_inline.is_valid():
			img_formset.save()
			product_category_form.save()

			stocks = stock_record_inline.save(commit=False)
			for stock in stocks:
				stock.seller = request.user
				stock.save()
				

		else:
			return self.render_to_response({
				"img_formset":img_formset, 
				"product_form":product_form,
				"product_category_form":product_category_form,
				"stock_record_inline":stock_record_inline
				})

		return redirect("products")


