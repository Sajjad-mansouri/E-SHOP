from django.db.models import Avg, Max, Case, When, Value, CharField, F
from decimal import Decimal


class Sorting:

	def apply_sorting(self, stocks):
		sort_by = self.get_order_by()
		stocks = stocks.order_by(*sort_by)
		return stocks

	def get_order_by(self):
		self.user_sort_by = self.request.GET.get("sort-by", "best-selling")
		if self.user_sort_by == "best-selling":
			sort_by = ["-sold"]

		elif self.user_sort_by == "price-low":
			sort_by = ["price"]

		elif self.user_sort_by == "price-high":
			sort_by = ["-price"]

		elif self.user_sort_by == "rating":
			sort_by = ["-rating"]

		elif self.user_sort_by == "newest":
			sort_by = ["date_created"]

		elif self.user_sort_by == "oldest":
			sort_by = ["-date_created"]

		elif self.user_sort_by == "discount":
			sort_by = ["-offer_discount", "-discount"]
		else:
			sort_by = ["-sold"]
		return sort_by




class AjaxResponse:
	def render_to_response(self, *args, **kwargs):
		self.is_ajax = self.request.headers.get('AJAX')
		if self.is_ajax:
			self.template_name = self.AJAX_template_name
		return super().render_to_response(*args, **kwargs)

class AjaxSortingResponse(Sorting, AjaxResponse):
	pass

class StockContexMixin:
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		agg =self.object_list.aggregate(max_price=Max("price"))
		max_price = agg["max_price"]
		brands = self.object_list.values_list("product__brand", flat=True).distinct()
		colors = self.object_list.values_list("product__color", flat=True).distinct()


		context["max_price"] = max_price
		context["colors"] = colors
		context["brands"] = brands
		context['order_by'] = self.user_sort_by
		return context