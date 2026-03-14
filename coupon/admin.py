from django.contrib import admin
from .models import Coupon, CouponApplication

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
	list_display = ["code", "valid_from", "valid_to", "discount"]


@admin.register(CouponApplication)
class CouponApplicationAdmin(admin.ModelAdmin):
	list_display = ["user", "coupon", "created"]
