from django.http import JsonResponse

class DeleteMixin:
	def form_valid(self, form):
		self.object.delete()
		return JsonResponse({"status":True})

	def form_invalid(self, form):
		return JsonResponse({"status":False})