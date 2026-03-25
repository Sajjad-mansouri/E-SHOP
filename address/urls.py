from django.urls import path
from .views import CreateAddressView

app_name = "address"
urlpatterns = [
	path("new_address/", CreateAddressView.as_view(), name="new_address")
]