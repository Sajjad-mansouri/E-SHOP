from django.shortcuts import render
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from .models import Address
from .forms import AddressForm


class AddressesMixin:
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['addresses'] = Address.objects.filter(user=self.request.user)
		return context

class AddressCreateView(AddressesMixin, CreateView):
	model = Address
	form_class = AddressForm
	template_name = "address/manage_address.html"
	success_url = reverse_lazy("address:new_address")


	def form_valid(self, form):
		if self.request.user.is_authenticated:
			form.instance.user = self.request.user

		return super().form_valid(form)


class AddressUpdateView(AddressesMixin, UpdateView):
	model = Address
	form_class = AddressForm
	template_name = "address/manage_address.html"
	success_url = reverse_lazy("address:new_address")

