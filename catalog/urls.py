from django.urls import path
from .views import HomePageView, ProductDetailView

urlpatterns = [
	path("", HomePageView.as_view(), name="home"),
	path("<slug:slug>/<int:stock_id>/", ProductDetailView.as_view(), name="product_detail"),

]