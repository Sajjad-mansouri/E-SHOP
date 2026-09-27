from django.urls import path

from . import views

app_name = "payment"
urlpatterns = [
    path("success/", views.SuccessPayment.as_view(), name="success"),
    path("cancel/", views.CancelPayment.as_view(), name="success"),
]
