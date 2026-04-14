from django.urls import path
from . import views

app_name = "catalog"
urlpatterns = [
	path("", views.HomePageView.as_view(), name="home"),
	path("filter/<int:product_class>/", views.CategoryFilter.as_view(), name="category_product_filter"),
	path("apply_rating/", views.ApplyRating.as_view(), name="apply_rating"),
	path("<slug:slug>/<int:stock_id>/", views.ProductDetailView.as_view(), name="product_detail"),
	path("offer/<slug:slug>/", views.OfferProductListView.as_view(), name="offer_products"),

	path("<slug:category>/", views.CategoryProducts.as_view(), name="category"),

]