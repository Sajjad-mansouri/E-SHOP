from django.urls import path
from .views import dashboard, ProductListView, CreateUpdateProductView

urlpatterns = [
	path("", dashboard, name="dashboard"),
	path("products/", ProductListView.as_view(), name="products"),
	path("product/create/", CreateUpdateProductView.as_view(), name="create_product"),
	path("product/update/<int:id>/", CreateUpdateProductView.as_view(), name="update_product"),



]