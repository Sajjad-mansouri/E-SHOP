from django.urls import path
from . import views

app_name = "catalog"
urlpatterns = [
	path("", views.HomePageView.as_view(), name="home"),
	path("apply_rating/", views.ApplyRating.as_view(), name="apply_rating"),
	path("<slug:category>/", views.CategoryProducts.as_view(), name="category"),
	path("<slug:slug>/<int:stock_id>/", views.ProductDetailView.as_view(), name="product_detail"),
	path("offer/<slug:slug>/", views.OfferProductListView.as_view(), name="offer_products"),

]