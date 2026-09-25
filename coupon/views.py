from django.http import JsonResponse
from django.views.generic.base import TemplateResponseMixin, View

from .models import Coupon, CouponApplication

# Create your views here.


class ApplyCoupon(TemplateResponseMixin, View):
    def post(self, request, *args, **kwargs):
        coupon = self.get_coupon(request)
        is_valid = self.is_valid(request, coupon)
        discount = None
        if is_valid:
            discount = coupon.discount
        return JsonResponse({"is_valid": is_valid, "discount": discount})

    def get_coupon(self, request):
        code = request.POST.get("coupon")
        try:
            coupon = Coupon.objects.get(code=code)
        except Coupon.DoesNotExist:
            coupon = None

        return coupon

    def is_valid(self, request, coupon):
        if coupon:
            is_active = coupon.is_active
            if is_active:
                user_check = self.check_application_usage(request, coupon)
                return user_check
            else:
                return False

    def check_application_usage(self, request, coupon):
        usage = coupon.usage
        if usage == "Single use":
            if CouponApplication.objects.filter(coupon=coupon).exists():
                return False
            else:
                return True

        elif usage == "Multi-use":
            return True

        elif usage == "Once per customer":
            if CouponApplication.objects.filter(
                user=request.user, coupon=coupon
            ).exists():
                return False
            else:
                return True
