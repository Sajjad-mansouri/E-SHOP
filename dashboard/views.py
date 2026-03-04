from django.shortcuts import render
from django.views.generic.list import ListView
from stock.models import StockRecord

# Create your views here.
def dashboard(request):
	context = {}
	return render(request, "dashboard/main.html",context)


class ProductListView(ListView):
	template_name = "dashboard/product_list.html"
	model = StockRecord