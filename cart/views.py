from django.shortcuts import render
from django.views.generic.base import View
from django.http import JsonResponse
from .models import Cart, CartItem
from .forms import CartItemForm

# Create your views here.
class AddToCartView(View):

	def post(self, request, *args, **kwargs):
		if request.user.is_authenticated:
			cart_item_form = CartItemForm(request.POST)
			if cart_item_form.is_valid():
				try:
					cart = Cart.objects.get(submited=True)
				except Cart.DoesNotExist:
					cart = Cart.objects.create(user=request.user)
				cart_item = cart_item_form.save(commit=False)
				cart_item.cart = cart
				cart_item.save()
				return JsonResponse({"add":True})

			else:
				return JsonResponse({"errors":cart_item_form.errors})
