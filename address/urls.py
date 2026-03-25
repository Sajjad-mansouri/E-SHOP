from django.urls import path
from .views import AddressCreateView, AddressUpdateView

app_name = "address"
urlpatterns = [
	path("new/", AddressCreateView.as_view(), name="new_address"),
	path("update/<int:pk>", AddressUpdateView.as_view(), name="update_address"),

]