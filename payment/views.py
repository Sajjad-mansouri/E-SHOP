from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic.base import View

from order.models import Order

from .models import Payment


class Checkout(View):
    def get(self, request, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, status="pending")
        return render(request, "payment/checkout.html", {"order": order})

    def post(self, request, *args, **kwargs):
        order_id = int(request.POST.get("order"))
        try:
            order = Order.objects.get(id=order_id)
            Payment.objects.create(
                order=order, amount=order.calc_total_cost, status="SUCCESS"
            )
            cart = order.cart
            cart.submited = True
            cart.save()
            order.status = "paid"
            order.save()
            return JsonResponse({"status": True})

        except Order.DoesNotExist:
            return JsonResponse({"status": False})


class CheckoutConfirmation(View):
    def get(self, request, *args, **kwargs):
        order = Order.objects.filter(user=request.user, status="paid")[0]

        return render(request, "payment/confirmation.html", {"order": order})
