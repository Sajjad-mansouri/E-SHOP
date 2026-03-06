from django.urls import path
from .views import dashboard, ProductListView, CreateProductView

urlpatterns = [
	path("", dashboard, name="dashboard"),
	path("products/", ProductListView.as_view(), name="products"),
	path("product/create/", CreateProductView.as_view(), name="create_product"),


]