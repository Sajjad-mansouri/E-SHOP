from django.urls import path
from . import views


app_name = "dashboard"
urlpatterns = [
	path("overview/", views.DashboardOverView.as_view(), name="overview"),
	path("catalog/products/", views.ProductListView.as_view(), name="products"),
	path("catalog/product/create/", views.CreateUpdateProductView.as_view(), name="create_product"),
	path("catalog/product/update/<int:pk>/", views.CreateUpdateProductView.as_view(), name="update_product"),
	path("catalog/product/delete/<int:pk>/", views.DeleteProductView.as_view(), name="delete_product"),
	path("catalog/product/search", views.SearchProduct.as_view(), name="search_product"),

	path("catalog/product-type/", views.ProductTypeView.as_view(), name="product_type_list"),
	path("catalog/product-type/create/", views.ProductTypeCreateUpdateView.as_view(), name="product_type_create"),
	path("catalog/product-type/update/<int:pk>/", views.ProductTypeCreateUpdateView.as_view(), name="product_type_update"),
	path("catalog/product-type/delete/<int:pk>/", views.ProductTypeDeleteView.as_view(), name="product_type_delete"),

	path("catalog/applied_offers/", views.AppliedOfferListView.as_view(), name="applied_offers"),
	path("catalog/applied_offers/apply_offer/", views.AppliedOfferCreateView.as_view(), name="apply_offer"),
	path("catalog/applied_offers/remove/<int:pk>/", views.AppliedOfferDeleteView.as_view(), name="remove_applied_offer"),





	path("catalog/categories/", views.CategoryListView.as_view(), name="categories"),
	path("catalog/category/<int:pk>/", views.SubCategoryView.as_view(), name="sub_category"),
	path("catalog/category/create/", views.CategoryCreateView.as_view(), name="category_create"),
	path("catalog/category/update/<int:pk>/", views.CategoryUpdateView.as_view(), name="category_update"),
	path("catalog/category/delete/<int:pk>/", views.CategoryDeleteView.as_view(), name="category_delete"),

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
	path("customer/<int:pk>/", views.CustomerDetailView.as_view(), name="customer"),
	path("customer/<int:pk>/addresses", views.AddressListView.as_view(), name="addresses"),

	path("report/sales/", views.SalesReport.as_view(), name="sales_report"),

	path("content/reviews/", views.ReviewListView.as_view(), name="reviews"),
	path("content/review/update/<int:pk>/", views.ReviewStatusUpdateView.as_view(), name="review_update"),
	path("content/review/delete/<int:pk>/", views.ReviewDeletView.as_view(), name="review_delete"),



	path("collection/product_group/", views.ProductGroupListView.as_view(), name="product_group"),
	path("collection/product_group/create/", views.ProductGroupCreateView.as_view(), name="product_group_create"),
	path("collection/product_group/update/<int:pk>/", views.ProductGroupUpdateView.as_view(), name="product_group_update"),
	path("collection/product_group/delete/<int:pk>/", views.ProductGroupDeleteView.as_view(), name="product_group_delete"),

	path("collection/collection_list/", views.CollectionListView.as_view(), name="collection_list"),
	path("collection/collection_list/delete/<int:pk>/", views.CollectionListDeleteView.as_view(), name="collection_list_delete"),
	path("collection/collection_list/create/", views.CollectionListCreateView.as_view(), name="collection_list_create"),
	path("collection/collection_list/update/<int:pk>/", views.CollectionListUpdateView.as_view(), name="collection_list_update"),







]