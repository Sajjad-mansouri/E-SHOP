from django.shortcuts import render,redirect,get_object_or_404
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.base import View, TemplateResponseMixin
from django.views.generic.edit import DeleteView, CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.forms.models import inlineformset_factory
from .wizard_views import OfferWizardStepView
from .forms import (
					image_formset, 
					ProductForm, 
					ProductCategoryInline, 
					StockRecordInlineForm, 
					ProductClassForm,
					ProductTypeForm,
					product_type_attr_formset,
					CategoryForm,

					OfferRangeForm,
					OfferDetailForm,
					OfferTypeForm,
					OfferRestrictionForm,

					CouponForm,
					)
from stock.models import StockRecord
from catalog.models import Product, ProductClass, ProductAttribute, ProductAttributeValue, Category
from offer.models import OfferRange, Offer
from coupon.models import Coupon

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
		product_id = kwargs.get('pk')
		if product_id:
			self.product = get_object_or_404(Product, id=product_id)
			self.product_class = self.product.product_class

		elif product_class_id:
			self.product_class = get_object_or_404(ProductClass, id=product_class_id)
			self.product=None

		else:
			self.product_class = None
			self.product=None


		return super().dispatch(request, *args, **kwargs)

	def get(self, request, *args, **kwargs):

		img_formset = image_formset(instance=self.product, prefix="img")
		product_form = ProductForm(self.product_class , instance=self.product,prefix="product")

		product_category_form = ProductCategoryInline(instance=self.product, prefix="category")
		stock_record_inline = StockRecordInlineForm(instance=self.product, prefix="stock")
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




class DeleteProductView(DeleteView):
	template_name = "dashboard/delete_product.html"
	model = Product
	success_url = reverse_lazy("products")


class SearchProduct(View):

	def get(self, request, *args, **kwargs):
		search = request.GET.get("search")
		object_list = StockRecord.objects.filter(
			Q(product__title__icontains=search)|
			Q(product__upc__icontains=search)
			)
		if object_list:
			return render(request, "dashboard/_records.html", {"object_list":object_list, "search":True})
		else:
			return HttpResponse("")


class ProductTypeView(ListView):
	model = ProductClass
	template_name = "dashboard/product_type/product_type_list.html"


class ProductTypeCreateUpdateView(UpdateView):
	model = ProductClass
	form_class = ProductTypeForm
	template_name = "dashboard/product_type/product_type_create_update.html"
	success_url = reverse_lazy("product_type_list")


	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["attrs_formset"] = self.get_formset()
		return context


	def post(self, request, *args, **kwargs):
		"""
		Handle POST requests: instantiate a form instance with the passed
		POST variables and then check if it's valid.
		"""
		self.object = self.get_object()
		form = self.get_form()
		if form.is_valid():
			self.object = form.save(commit=False)
		formset = self.get_formset()

		if form.is_valid() and formset.is_valid():
			return self.form_valid(form, formset)
		else:

			return self.form_invalid(form, formset)

	def get_object(self):

		product_type_pk = self.kwargs.get("pk")
		if product_type_pk:

			return  get_object_or_404(ProductClass, pk=product_type_pk)
		else:
			return  None


	def get_formset(self):

		return product_type_attr_formset(**self.get_form_kwargs())

	def form_valid(self, form, formset):
		success_url = self.get_success_url()
		self.object = form.save()
		formset.save()
		return HttpResponseRedirect(success_url)

	def form_invalid(self, form, formset):
		return self.render_to_response(self.get_context_data(form=form, formset=formset))


class ProductTypeDeleteView(DeleteView):
	template_name = "dashboard/product_type/delete_product_type.html"
	model = ProductClass
	success_url = reverse_lazy("product_type_list")


class CategoryListView(ListView):
	template_name = "dashboard/category/category_list.html"
	model = Category

class SubCategoryView(DetailView):
	template_name = "dashboard/category/category_list.html"
	model = Category


class CategoryCreateView(CreateView):
	template_name = "dashboard/category/category_create_update.html"
	model = Category
	form_class = CategoryForm
	success_url = reverse_lazy("category")

class CategoryUpdateView(UpdateView):
	template_name = "dashboard/category/category_create_update.html"
	model = Category
	form_class = CategoryForm
	success_url = reverse_lazy("category")

class CategoryDeleteView(DeleteView):
	template_name = "dashboard/category/category_delete.html"
	model = Category
	success_url = reverse_lazy("category")



class OfferRangeListView(ListView):
	model = OfferRange
	template_name = "dashboard/offer/range/list.html"


class OfferRangeCreateView(CreateView):
	model = OfferRange
	template_name = "dashboard/offer/range/create_update.html"
	form_class = OfferRangeForm
	success_url = reverse_lazy("offer_range")

class OfferRangeUpdateView(UpdateView):
	model = OfferRange
	template_name = "dashboard/offer/range/create_update.html"
	form_class = OfferRangeForm
	success_url = reverse_lazy("offer_range")

class OfferRangeDeleteView(DeleteView):
	model = OfferRange
	template_name = "dashboard/offer/range/delete.html"
	success_url = reverse_lazy("offer_range")


class OfferListView(ListView):
	model = Offer
	template_name = "dashboard/offer/offer/list.html"


class CreateOfferView(OfferWizardStepView):

	template_name = "dashboard/offer/offer/create_update.html"


class OfferStepView(View):
	def get(self, request, *args, **kwargs):
		offer_step = kwargs.get("offer_step")
		offer_pk = kwargs.get('offer_pk')
		if offer_pk:
			offer = get_object_or_404(Offer, pk=offer_pk)
			offer_type = offer.offer_type
		else:
			offer=None
			offer_type=None

		if offer_step==1:
			form = OfferDetailForm(instance=offer)
		elif offer_step == 2:
			form = OfferTypeForm(instance=offer_type)
		elif offer_step == 3:
			form = OfferRestrictionForm(instance=offer)
		return render(request, f"dashboard/offer/offer/_step_{offer_step}.html", {"form":form})



class UpdateOfferView(CreateOfferView):
	update = True

class DeleteOfferView(DeleteView):
	template_name = "dashboard/offer/offer/delete.html"
	model = Offer
	success_url = reverse_lazy("dashboard:offer_list")

	def form_valid(self, form):
		success_url = self.get_success_url()
		self.object.offer_type.delete()
		return HttpResponseRedirect(success_url)


class CouponListView(ListView):
	model = Coupon
	template_name = "dashboard/offer/coupon/list.html"

class CouponCreateView(CreateView):
	model = Coupon
	form_class = CouponForm
	success_url = reverse_lazy("dashboard:coupon_list")
	template_name = "dashboard/offer/coupon/create_update.html"

class CouponUpdateView(UpdateView):
	model = Coupon
	form_class = CouponForm
	success_url = reverse_lazy("dashboard:coupon_list")
	template_name = "dashboard/offer/coupon/create_update.html"

class CouponDeleteView(DeleteView):
	model = Coupon
	success_url = reverse_lazy("dashboard:coupon_list")
	template_name = "dashboard/offer/coupon/delete.html"