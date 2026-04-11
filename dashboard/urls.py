from django.urls import path
from . import views


app_name = "dashboard"
urlpatterns = [
	path("overview/", views.DashboardOverView.as_view(), name="overview"),
	path("products/", views.ProductListView.as_view(), name="products"),
	path("product/create/", views.CreateUpdateProductView.as_view(), name="create_product"),
	path("product/update/<int:pk>/", views.CreateUpdateProductView.as_view(), name="update_product"),
	path("product/delete/<int:pk>/", views.DeleteProductView.as_view(), name="delete_product"),
	path("product/search", views.SearchProduct.as_view(), name="search_product"),

	path("product-type/", views.ProductTypeView.as_view(), name="product_type_list"),
	path("product-type/create/", views.ProductTypeCreateUpdateView.as_view(), name="product_type_create"),
	path("product-type/update/<int:pk>/", views.ProductTypeCreateUpdateView.as_view(), name="product_type_update"),
	path("product-type/delete/<int:pk>/", views.ProductTypeDeleteView.as_view(), name="product_type_delete"),


	path("categories/", views.CategoryListView.as_view(), name="categories"),
	path("category/<int:pk>/", views.SubCategoryView.as_view(), name="sub_category"),
	path("category/create/", views.CategoryCreateView.as_view(), name="category_create"),
	path("category/update/<int:pk>/", views.CategoryUpdateView.as_view(), name="category_update"),
	path("category/delete/<int:pk>/", views.CategoryDeleteView.as_view(), name="category_delete"),

	path("offer/range/", views.OfferRangeListView.as_view(), name="offer_range"),
	path("offer/range/create/", views.OfferRangeCreateView.as_view(), name="offer_range_create"),
	path("offer/range/update/<int:pk>/", views.OfferRangeUpdateView.as_view(), name="offer_range_update"),
	path("offer/range/delete/<int:pk>/", views.OfferRangeDeleteView.as_view(), name="offer_range_delete"),

	path("offer/", views.OfferListView.as_view(), name="offer_list"),

	path("offer/create/", views.CreateOfferView.as_view(), name="offer_create"),
	path("offer/create/<int:offer_step>/", views.CreateOfferView.as_view(), name="offer_step_create"),
	path("offer/<int:offer_step>/", views.OfferStepView.as_view(), name="offer_form"),

	path("offer/update/<int:offer_pk>/", views.UpdateOfferView.as_view(), name="offer_update"),
	path("offer/update/<int:offer_pk>/<int:offer_step>/", views.UpdateOfferView.as_view(), name="offer_step_update"),
	path("offer/<int:offer_pk>/<int:offer_step>/", views.OfferStepView.as_view(), name="update_offer_form"),

	path("offer/delete/<int:pk>/", views.DeleteOfferView.as_view(), name="delete_offer"),


	path("offer/coupon/", views.CouponListView.as_view(), name="coupon_list"),
	path("offer/coupon/create/", views.CouponCreateView.as_view(), name="coupon_create"),
	path("offer/coupon/update/<int:pk>/", views.CouponUpdateView.as_view(), name="coupon_update"),
	path("offer/coupon/delete/<int:pk>/", views.CouponDeleteView.as_view(), name="coupon_delete"),

	path("fulfilment/orders/", views.OderListView.as_view(), name="order_list"),
	path("fulfilment/order/<int:pk>/", views.OderDetailView.as_view(), name="order_detail"),

	path("fulfilment/statistics/", views.FulfilmentStatistic.as_view(), name="statistics"),

	path("customers/", views.CustomerListView.as_view(), name="customers"),


















	







]