# Create your views here.
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class SuccessPayment(LoginRequiredMixin, TemplateView):
    template_name = "payment/success_payment.html"


class CancelPayment(LoginRequiredMixin, TemplateView):
    template_name = "payment/cancel_payment.html"
