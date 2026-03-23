from django.urls import path
from .views import HomePageView, ProductDetailView, CategoryProducts

app_name = "catalog"
urlpatterns = [
	path("", HomePageView.as_view(), name="home"),
	path("<slug:category>/", CategoryProducts.as_view(), name="category"),
	path("<slug:slug>/<int:stock_id>/", ProductDetailView.as_view(), name="product_detail"),


]