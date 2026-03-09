from django.urls import path
from .views import (
					dashboard, 
					ProductListView, 
					CreateUpdateProductView, 
					DeleteProductView, 
					SearchProduct,
					ProductTypeView,
					ProductTypeCreateUpdateView,
					ProductTypeDeleteView
					)

urlpatterns = [
	path("", dashboard, name="dashboard"),
	path("products/", ProductListView.as_view(), name="products"),
	path("product/create/", CreateUpdateProductView.as_view(), name="create_product"),
	path("product/update/<int:pk>/", CreateUpdateProductView.as_view(), name="update_product"),
	path("product/delete/<int:pk>/", DeleteProductView.as_view(), name="delete_product"),
	path("product/search", SearchProduct.as_view(), name="search_product"),

	path("product-type/", ProductTypeView.as_view(), name="product_type_list"),
	path("product-type/create/", ProductTypeCreateUpdateView.as_view(), name="product_type_create"),
	path("product-type/update/<int:pk>/", ProductTypeCreateUpdateView.as_view(), name="product_type_update"),
	path("product-type/delete/<int:pk>/", ProductTypeDeleteView.as_view(), name="product_type_delete"),

	







]