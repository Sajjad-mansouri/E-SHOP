from django.shortcuts import render
from django.views.generic.base import View, TemplateResponseMixin
from django.http import JsonResponse
from django.db.models import F
from .models import Cart, CartItem
from .forms import CartItemForm

# Create your views here.
class AddToCartView(View):

	def post(self, request, *args, **kwargs):
		if request.user.is_authenticated:
			cart_item_form = CartItemForm(request.POST)
			if cart_item_form.is_valid():
				try:
					cart = Cart.objects.get(submited=False)
				except Cart.DoesNotExist:
					cart = Cart.objects.create(user=request.user)
				cart_item = cart_item_form.save(commit=False)
				cart_item.cart = cart
				cart_item.save()
				return JsonResponse({"status":True, "type":"add"})

			else:
				return JsonResponse({"errors":cart_item_form.errors})


class RemoveFromCartView(View):
	def post(self, request, *args, **kwargs):
		if request.user.is_authenticated:
			cart_item_form = CartItemForm(request.POST)
			if cart_item_form.is_valid():
				stock_pk = cart_item_form.cleaned_data["stock"]
				try:

					cart = Cart.objects.get(submited=False)
					cart_item = CartItem.objects.get(stock=stock_pk, cart=cart)
					cart_item.delete()

					return JsonResponse({"status":True, "type":"remove"})

				except (Cart.DoesNotExist,CartItem.DoesNotExist):
					pass	

			else:
				return JsonResponse({"errors":cart_item_form.errors})

class CartView(TemplateResponseMixin, View):
	template_name = "cart/items.html"


	def get(self, request, *args, **kwargs):
		if request.user.is_authenticated:
			try:
				cart = Cart.objects.get(submited=False)
			except Cart.DoesNotExist:
				cart = Cart.objects.create(user=request.user)

			cart_items = cart.items.all()
		else:
			cart_items = []
		return self.render_to_response({"items":cart_items, "cart":cart})


class CartItemQuantity(View):
	def post(self, request, *args, **kwargs):
		cart_item_id = int(request.POST.get('id'))
		func = request.POST.get('func')
		try:
			cart_item = CartItem.objects.get(id=cart_item_id)
			if func == "plus":
				cart_item.quantity = F("quantity") + 1
			elif func == "minus":
				cart_item.quantity = F("quantity") - 1
			cart_item.save()

			return JsonResponse({"status":True}) 
		except CartItem.DoesNotExist:
			return JsonResponse({"status":False}) 
