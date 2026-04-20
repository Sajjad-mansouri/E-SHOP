from django.db.models import Q
from django.http import JsonResponse
from stock.models import StockRecord

class DeleteMixin:
	def form_valid(self, form):
		self.object.delete()
		return JsonResponse({"status":True})

	def form_invalid(self, form):
		return JsonResponse({"status":False})


class StockRecordContexMixin:
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["stock_records"] = StockRecord.objects.filter(seller=self.request.user)
		return context

class FormHandlerMixin:

	def form_valid(self, form):
		form.save()
		return JsonResponse({"status":True})

	def form_invalid(self, form):
		errors = self.serialize_errors(form)
		return JsonResponse({"status":False, "errors":errors})

	def serialize_errors(self, form):
		errors = form.errors.get_json_data()
		return errors


class collectionMixin:
	def get_queryset(self):
		qs = super().get_queryset()
		qs = self.apply_filter(qs)
		qs = self.search(qs)
		return qs

	def apply_filter(self, qs):
		status = self.request.GET.get("status")
		query = Q()
		if status != "all" and status:

			query = Q(status=status)
		return qs.filter(query)

	def search(self, qs):
		search = self.request.GET.get("search")
		query = Q()
		if search:
			query = Q(name__icontains=search)

		return qs.filter(query)