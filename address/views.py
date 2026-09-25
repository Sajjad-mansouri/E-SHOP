from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from .forms import AddressForm
from .models import Address


class AddressesMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["addresses"] = Address.objects.filter(user=self.request.user)
        return context


class AddressCreateView(AddressesMixin, CreateView):
    model = Address
    form_class = AddressForm
    template_name = "address/manage_address.html"
    success_url = reverse_lazy("address:new_address")

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.user = self.request.user
        form.save()
        return JsonResponse({"status": True, "created": True})

    def form_invalid(self, form):
        return JsonResponse({"status": False, "error": form.errors, "created": True})


class AddressUpdateView(AddressesMixin, UpdateView):
    model = Address
    form_class = AddressForm
    template_name = "address/manage_address.html"
    success_url = reverse_lazy("address:new_address")

    def form_valid(self, form):
        form.save()
        return JsonResponse({"status": True, "created": False})

    def form_invalid(self, form):
        return JsonResponse({"status": False, "error": form.errors, "created": False})


class AddressDeleteView(DeleteView):
    model = Address

    def form_valid(self, form):
        if self.object:
            self.object.delete()
            return JsonResponse({"status": True})
        else:
            return JsonResponse({"status": False})

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        obj_id = self.request.POST.get("id")
        try:
            obj = queryset.get(id=obj_id)
        except queryset.model.DoesNotExist:
            obj = None
        return obj
