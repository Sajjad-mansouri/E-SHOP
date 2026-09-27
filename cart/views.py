from django.db.models import F
from django.http import JsonResponse
from django.views.generic.base import TemplateResponseMixin, View

from .forms import CartItemForm
from .models import Cart, CartItem


class AddToCartView(View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"status": False}, status=401)

        cart_item_form = CartItemForm(request.POST)

        if not cart_item_form.is_valid():
            return JsonResponse(
                {
                    "status": False,
                    "errors": cart_item_form.errors,
                },
                status=400,
            )

        cart, _ = Cart.objects.get_or_create(
            user=request.user,
            submited=False,
        )

        cart_item = cart_item_form.save(commit=False)
        cart_item.cart = cart
        cart_item.save()

        return JsonResponse({"status": True, "type": "add"})


class RemoveFromCartView(View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"status": False}, status=401)

        cart_item_form = CartItemForm(request.POST)

        if not cart_item_form.is_valid():
            return JsonResponse(
                {
                    "status": False,
                    "errors": cart_item_form.errors,
                },
                status=400,
            )

        stock = cart_item_form.cleaned_data["stock"]

        try:
            cart = Cart.objects.get(
                user=request.user,
                submited=False,
            )
            cart_item = CartItem.objects.get(
                stock=stock,
                cart=cart,
            )
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            return JsonResponse({"status": False})

        cart_item.delete()

        return JsonResponse({"status": True, "type": "remove"})


class CartView(TemplateResponseMixin, View):
    template_name = "cart/items.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(
                user=request.user,
                submited=False,
            )
            cart_items = cart.items.all()
        else:
            cart = None
            cart_items = []

        return self.render_to_response(
            {
                "items": cart_items,
                "cart": cart,
            }
        )


class ModifyCartItemView(View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"status": False}, status=401)

        try:
            cart_item_id = int(request.POST.get("id"))
        except (TypeError, ValueError):
            return JsonResponse({"status": False}, status=400)

        func = request.POST.get("func")

        try:
            cart_item = CartItem.objects.get(
                id=cart_item_id,
                cart__user=request.user,
                cart__submited=False,
            )
        except CartItem.DoesNotExist:
            return JsonResponse({"status": False})

        if func == "plus":
            cart_item.quantity = F("quantity") + 1
            cart_item.save(update_fields=["quantity"])
        elif func == "minus":
            cart_item.quantity = F("quantity") - 1
            cart_item.save(update_fields=["quantity"])
        elif func == "remove":
            cart_item.delete()
        else:
            return JsonResponse({"status": False}, status=400)

        return JsonResponse({"status": True})
