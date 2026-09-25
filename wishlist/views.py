from django.http import JsonResponse
from django.views.generic.base import View

from stock.models import StockRecord

from .models import WishList


# Create your views here.
class WishListCreateView(View):
    def post(self, request, *args, **kwargs):
        stock = int(request.POST.get("stock"))
        func_type = request.POST.get("funcType")
        stock_record = StockRecord.objects.get(id=stock)
        if func_type == "add":
            WishList.objects.create(user=request.user, stock_record=stock_record)
        elif func_type == "remove":
            WishList.objects.filter(
                user=request.user, stock_record=stock_record
            ).delete()
        return JsonResponse({"status": True})
