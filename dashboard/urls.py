from django.urls import path
from .views import (
					dashboard, 
					ProductListView, 
					CreateUpdateProductView, 
					DeleteProductView, 
					SearchProduct,
					ProductTypeView,
					ProductTypeCreateUpdateView,
					ProductTypeDeleteView,

					CategoryListView,
					SubCategoryView,
					CategoryCreateView,
					CategoryUpdateView,
					CategoryDeleteView,

					OfferRangeListView,
					OfferRangeCreateView,
					OfferRangeUpdateView,
					OfferRangeDeleteView,

					OfferListView,
					CreateOfferView,
					OfferStepView,
					UpdateOfferView,
					DeleteOfferView,


					CouponListView,
					CouponCreateView,
					CouponUpdateView
					)


app_name = "dashboard"
urlpatterns = [
	path("", dashboard, name="main"),
	path("products/", ProductListView.as_view(), name="products"),
	path("product/create/", CreateUpdateProductView.as_view(), name="create_product"),
	path("product/update/<int:pk>/", CreateUpdateProductView.as_view(), name="update_product"),
	path("product/delete/<int:pk>/", DeleteProductView.as_view(), name="delete_product"),
	path("product/search", SearchProduct.as_view(), name="search_product"),

	path("product-type/", ProductTypeView.as_view(), name="product_type_list"),
	path("product-type/create/", ProductTypeCreateUpdateView.as_view(), name="product_type_create"),
	path("product-type/update/<int:pk>/", ProductTypeCreateUpdateView.as_view(), name="product_type_update"),
	path("product-type/delete/<int:pk>/", ProductTypeDeleteView.as_view(), name="product_type_delete"),


	path("category/", CategoryListView.as_view(), name="category"),
	path("category/<int:pk>/", SubCategoryView.as_view(), name="sub_category"),
	path("category/create/", CategoryCreateView.as_view(), name="category_create"),
	path("category/update/<int:pk>/", CategoryUpdateView.as_view(), name="category_update"),
	path("category/delete/<int:pk>/", CategoryDeleteView.as_view(), name="category_delete"),

	path("offer/range/", OfferRangeListView.as_view(), name="offer_range"),
	path("offer/range/create/", OfferRangeCreateView.as_view(), name="offer_range_create"),
	path("offer/range/update/<int:pk>/", OfferRangeUpdateView.as_view(), name="offer_range_update"),
	path("offer/range/delete/<int:pk>/", OfferRangeDeleteView.as_view(), name="offer_range_delete"),

	path("offer/", OfferListView.as_view(), name="offer_list"),

	path("offer/create/", CreateOfferView.as_view(), name="offer_create"),
	path("offer/create/<int:offer_step>/", CreateOfferView.as_view(), name="offer_step_create"),
	path("offer/<int:offer_step>/", OfferStepView.as_view(), name="offer_form"),

	path("offer/update/<int:offer_pk>/", UpdateOfferView.as_view(), name="offer_update"),
	path("offer/update/<int:offer_pk>/<int:offer_step>/", UpdateOfferView.as_view(), name="offer_step_update"),
	path("offer/<int:offer_pk>/<int:offer_step>/", OfferStepView.as_view(), name="update_offer_form"),

	path("offer/delete/<int:pk>/", DeleteOfferView.as_view(), name="delete_offer"),


	path("offer/coupon/", CouponListView.as_view(), name="coupon_list"),
	path("offer/coupon/create/", CouponCreateView.as_view(), name="coupon_create"),
	path("offer/coupon/update/<int:pk>/", CouponUpdateView.as_view(), name="coupon_update"),













	







]