from django.core import serializers
from django.views.generic.edit import FormView
from django.http import JsonResponse
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect
from .forms import OfferDetailForm, OfferTypeForm, OfferRestrictionForm
class OfferWizardStepView(FormView):
	wizard_name = "offer"
	form_class = None
	update = False
	success_url = reverse_lazy("offer_list")

	def dispatch(self, request, *args, **kwargs):

		self.step = int(request.GET.get("step", 1))

		return super().dispatch(request, *args, **kwargs)

	def get_form_class(self):
		"""Return the form class to use."""

		if self.step == 1:

			return OfferDetailForm
		elif self.step == 2:

			return OfferTypeForm
		elif self.step == 3:
			return OfferRestrictionForm 


	def _store_object(self, form):
		self.step_name = f"step_{self.step}"
		session_data = self.request.session.setdefault(self.wizard_name, {})
		form = form.save(commit=False)
		data = serializers.serialize("json", [form])
		session_data[self.step_name] = data
		self.request.session.modified=True


	def _fetch_object(self, step):
		session_data = self.request.session.setdefault(self.wizard_name, {})
		qs_json = session_data.get(f"step_{step}")
		deserialised_qs = list(serializers.deserialize("json", qs_json))
		return deserialised_qs[0].object
			


	def form_invalid(self, form):
		return JsonResponse({"errors":form.errors})

	def form_valid(self, form):
		self._store_object(form)

		if self.update and "save" in form.data or self.step == 3:
			return self.save_offer()

		return JsonResponse({"is_valid":True})


	def save_offer(self):
		step = 1
		step1_model = self._fetch_object(step)

		step = 2
		step2_model = self._fetch_object(step)

		step = 3
		step3_model = self._fetch_object(step)
		step2_model.save()
		step1_model.max_discount = step3_model.max_discount
		step1_model.start_datetime = step3_model.start_datetime
		step1_model.end_datetime = step3_model.end_datetime
		step1_model.offer_type = step2_model
		step1_model.save()


		return JsonResponse({"is_valid":True})