from django.urls import path

from .views import ApplyCoupon

app_name = "coupon"
urlpatterns = [
    path("apply_coupon/", ApplyCoupon.as_view(), name="apply_coupon"),
]
