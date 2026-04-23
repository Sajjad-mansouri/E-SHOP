from django.urls import path
from . import views

app_name = "catalog"
urlpatterns = [
	path("", views.HomePageView.as_view(), name="home"),

	path("apply_rating/", views.ApplyRating.as_view(), name="apply_rating"),
	path("<slug:slug>/<int:stock_id>/", views.ProductDetailView.as_view(), name="product_detail"),
	path("offer/<slug:slug>/", views.OfferProductListView.as_view(), name="offer_products"),

	path("<slug:slug>/products/", views.CategoryProducts.as_view(), name="category_products"),
	path("<slug:slug>/products/page/<int:page>/", views.CategoryProducts.as_view(), name="category_page"),

	path("collection/<slug:slug>/", views.CollectionListView.as_view(), name="collection"),
	path("category/<slug:slug>/", views.SubCategoryListView.as_view(), name="sub_categories"),




]