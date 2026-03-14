from django.core import serializers
from django.views.generic.edit import FormView
from django.http import JsonResponse
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect, get_object_or_404
from .forms import OfferDetailForm, OfferTypeForm, OfferRestrictionForm
from offer.models import Offer
class OfferWizardStepView(FormView):
	wizard_name = "offer"
	form_class = None
	update = False
	success_url = reverse_lazy("offer_list")
	update = False

	def dispatch(self, request, *args, **kwargs):
		self.save = request.POST.get('save')
		self.step = kwargs.get('offer_step', 1)
		self.offer_pk = self.kwargs.get('offer_pk')
		return super().dispatch(request, *args, **kwargs)

	def _get_urls(self, step):
		if self.update:
			
			self.form_url = reverse("dashboard:update_offer_form", args=(self.offer_pk, step,))
			self.create_form_url = reverse("dashboard:offer_step_update",args=(self.offer_pk, step,))


		else:

			self.form_url = reverse("dashboard:offer_form", args=(step,))
			self.create_form_url = reverse("dashboard:offer_step_create",args=(step,))

	def get(self, request, *args, **kwargs):
		self._get_urls(self.step)
		return super().get(request, *args, **kwargs)

	def post(self, request, *args, **kwargs):
		self._get_urls(self.step+1)
		return super().post(request, *args, **kwargs)

	def get_form_class(self):
		"""Return the form class to use."""

		if self.step == 1:

			return OfferDetailForm
		elif self.step == 2:

			return OfferTypeForm
		elif self.step == 3:
			return OfferRestrictionForm 

	def get_form_kwargs(self):
		kwargs = super().get_form_kwargs()
		if self.update:
			obj = get_object_or_404(Offer, pk=self.offer_pk)
			if self.step in [1,3]:
				obj = obj
			elif self.step == 2:
				obj = obj.offer_type 
			kwargs.update({"instance": obj})
		return kwargs

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
		if qs_json:
			deserialised_qs = list(serializers.deserialize("json", qs_json))
			return deserialised_qs[0].object
			
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)


		context["form_url"] = self.form_url
		context["create_form_url"] = self.create_form_url
		context["update"] = self.update

		return context

	def form_invalid(self, form):
		return JsonResponse({"errors":form.errors})

	def form_valid(self, form):
		self._store_object(form)


		if (self.update and self.save=='true') or self.step == 3:
			return self.save_offer()

		return JsonResponse({"is_valid":True, 
							"form_url":self.form_url, 
							"create_form_url":self.create_form_url,
							})


	def save_offer(self):
		print('save offfer')
		step = 1
		step1_model = self._fetch_object(step)

		step = 2
		step2_model = self._fetch_object(step)

		step = 3
		step3_model = self._fetch_object(step)
		if step3_model:
			step1_model.max_discount = step3_model.max_discount
			step1_model.start_datetime = step3_model.start_datetime
			step1_model.end_datetime = step3_model.end_datetime
		if step2_model:
			step2_model.save()
			step1_model.offer_type = step2_model
		step1_model.save()


		return JsonResponse({"is_valid":True})