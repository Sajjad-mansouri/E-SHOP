from django.shortcuts import render,redirect,get_object_or_404
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.db.models import Q
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic.list import ListView
from django.views.generic.base import View, TemplateResponseMixin, TemplateView
from django.views.generic.edit import DeleteView, CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.forms.models import inlineformset_factory
from django.contrib.auth import get_user_model
from django.db.models import Sum
from .wizard_views import OfferWizardStepView
from .forms import (
					image_formset, 
					ProductForm, 
					ProductCategoryInline, 
					StockRecordInlineForm, 
					StockRecordForm,
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
from order.models import Order


UserModel = get_user_model()

# Create your views here.
class DashboardOverView(TemplateView):
	template_name = "dashboard/overview/overview.html"
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		customers = self.get_customers()
		stock_records = self.get_stock_products()
		orders = self.get_orders()
		today_orders = self.get_today_order()
		earns = self.get_revenue()

		context["customers"] = customers
		context["stock_records"] = stock_records
		context["orders"] = orders
		context["today_orders"] = today_orders
		context["earns"] = earns




		return context

	def get_customers(self):
		customers = UserModel.objects.filter(user_type="customer")
		return customers

	def get_stock_products(self):
		stock_records = StockRecord.objects.filter(is_public=True, num_in_stock__gt=0)
		return stock_records

	def get_orders(self):
		orders = Order.objects.all()
		return orders

	def get_today_order(self):
		today = timezone.now()
		orders = self.get_orders()
		today_orders = orders.filter(created_at__date=today)
		return today_orders

	def get_revenue(self):
		earns = 0
		orders = self.get_orders().filter(status__in=["paid", "shipped", "delivered"])
		for order in orders:
			earns += order.pure_price

		return earns


class ProductListView(ListView):
	template_name = "dashboard/product/products.html"
	model = StockRecord

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		product_class_form = ProductClassForm()
		context['product_class_form'] = product_class_form
		return context

class CreateUpdateProductView(TemplateResponseMixin, View):
	template_name = "dashboard/product/create_update.html"

	def dispatch(self, request, *args, **kwargs):
		product_class_id = request.GET.get('product_class')
		product_id = kwargs.get('pk')
		if product_id:
			self.stock = get_object_or_404(StockRecord, id=product_id)
			self.product = self.stock.product
			self.product_class = self.product.product_class

		elif product_class_id:
			self.product_class = get_object_or_404(ProductClass, id=product_class_id)
			self.product=None
			self.stock = None

		else:
			self.product_class = None
			self.product=None
			self.stock = None


		return super().dispatch(request, *args, **kwargs)

	def get(self, request, *args, **kwargs):

		img_formset = image_formset(instance=self.product, prefix="img")
		product_form = ProductForm(self.product_class , instance=self.product,prefix="product")

		product_category_form = ProductCategoryInline(instance=self.product, prefix="category")
		# stock_record_inline = StockRecordInlineForm(instance=self.product, prefix="stock")
		stock_record_form = StockRecordForm(instance=self.stock)

		return self.render_to_response({
			"img_formset":img_formset, 
			"product_form":product_form, 
			"product_category_form":product_category_form,
			"stock_record_form":stock_record_form,
			"product_class":self.product_class


			})

	def post(self, request, *args, **kwargs):

		product_form = ProductForm(self.product_class, instance=self.product, data=request.POST, prefix="product")
		if product_form.is_valid():
			
			self.object = product_form.save()
		else:

			return render(request, "dashboard/product/create_update.html", {
				"product_form":product_form,
				"img_formset":img_formset,
				"product_category_form":product_category_form,
				"stock_record_form":stock_record_form,
				}
				)

		img_formset = image_formset(data=request.POST,files=request.FILES,instance=self.object, prefix="img")
		product_category_form = ProductCategoryInline(data=request.POST,instance=self.object,  prefix="category")
		stock_record_form = StockRecordForm(data=request.POST, instance=self.stock)

		if img_formset.is_valid() and product_category_form.is_valid() and stock_record_form.is_valid():

			img_formset.save()
			product_category_form.save()

			stock = stock_record_form.save(commit=False)
			stock.product = self.object
			stock.seller = request.user
			stock.save()

				

		else:

			self.object.delete()
			return render(request, "dashboard/product/create_update.html", {
				"product_form":product_form,
				"img_formset":img_formset,
				"product_category_form":product_category_form,
				"stock_record_form":stock_record_form,

				})

		return redirect("dashboard:products")



class DeleteProductView(DeleteView):
	template_name = "dashboard/delete_product.html"
	model = Product
	success_url = reverse_lazy("dashboard:products")

	def form_valid(self, form):
		self.object.delete()

		return JsonResponse({"status":True})

	def form_invalid(self, form):
		return JsonResponse({"status":False})


class SearchProduct(View):

	def get(self, request, *args, **kwargs):
		search = request.GET.get("search")

		if search:	
			object_list = StockRecord.objects.filter(
				Q(product__title__icontains=search)|
				Q(product__upc__icontains=search)
				)

		else:
			object_list = StockRecord.objects.all()
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
	template_name = "dashboard/product_type/create_update.html"
	success_url = reverse_lazy("dashboard:product_type_list")


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
		formset = product_type_attr_formset(**self.get_form_kwargs())


		return formset

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

	def form_valid(self, form):
		self.object.delete()

		return JsonResponse({"status":True})

	def form_invalid(self, form):
		return JsonResponse({"status":False})

class CategoryListView(ListView):
	template_name = "dashboard/category/categories.html"
	model = Category

class SubCategoryView(DetailView):
	template_name = "dashboard/category/categories.html"
	model = Category


class CategoryCreateView(CreateView):
	template_name = "dashboard/category/create_update.html"
	model = Category
	form_class = CategoryForm
	success_url = reverse_lazy("dashboard:categories")

class CategoryUpdateView(UpdateView):
	template_name = "dashboard/category/create_update.html"
	model = Category
	form_class = CategoryForm
	success_url = reverse_lazy("dashboard:categories")


class CategoryDeleteView(DeleteView):
	template_name = "dashboard/category/category_delete.html"
	model = Category
	success_url = reverse_lazy("dashboard:categories")

	def form_valid(self, form):
		self.object.delete()

		return JsonResponse({"status":True})

	def form_invalid(self, form):
		return JsonResponse({"status":False})

class OfferRangeListView(ListView):
	model = OfferRange
	template_name = "dashboard/offer/range/list.html"


class OfferRangeCreateView(CreateView):
	model = OfferRange
	template_name = "dashboard/offer/range/create_update.html"
	form_class = OfferRangeForm
	success_url = reverse_lazy("dashboard:offer_range")

class OfferRangeUpdateView(UpdateView):
	model = OfferRange
	template_name = "dashboard/offer/range/create_update.html"
	form_class = OfferRangeForm
	success_url = reverse_lazy("dashboard:offer_range")
	search_template_name = "dashboard/offer/range/test.html"


class OfferRangeDeleteView(DeleteView):
	model = OfferRange
	template_name = "dashboard/offer/range/delete.html"
	success_url = reverse_lazy("offer_range")

	def form_valid(self, form):
		self.object.delete()
		return JsonResponse({"status":True})

	def form_invalid(self, form):
		return JsonResponse({"status":False})

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