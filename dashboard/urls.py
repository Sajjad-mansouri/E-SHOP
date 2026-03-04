from django.urls import path
from .views import dashboard, ProductListView

urlpatterns = [
	path("", dashboard, name="dashboard"),
	path("products/", ProductListView.as_view(), name="products"),

]