from django.urls import path
from .views import dashboard, ProductListView, CreateUpdateProductView, DeleteProductView, SearchProduct

urlpatterns = [
	path("", dashboard, name="dashboard"),
	path("products/", ProductListView.as_view(), name="products"),
	path("product/create/", CreateUpdateProductView.as_view(), name="create_product"),
	path("product/update/<int:pk>/", CreateUpdateProductView.as_view(), name="update_product"),
	path("product/delete/<int:pk>/", DeleteProductView.as_view(), name="delete_product"),
	path("product/search", SearchProduct.as_view(), name="search_product"),





]