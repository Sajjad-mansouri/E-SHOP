from decimal import ROUND_HALF_UP, Decimal

from django.db import transaction
from django.utils import timezone

from cart.models import Cart

from .models import Order, OrderItem

TWOPLACES = Decimal("0.01")


class OrderService:
    @classmethod
    @transaction.atomic
    def create_order(
        cls,
        *,
        user,
        cart,
        shipping_address,
        shipping_method,
        coupon_application=None,
        tax_rate=Decimal("0.00"),
    ):
        if not user.is_authenticated:
            raise ValueError("Authentication is required.")

        if cart.user_id != user.pk:
            raise ValueError("This cart does not belong to the user.")

        if not Decimal("0.00") <= tax_rate <= Decimal("100.00"):
            raise ValueError("Tax rate must be between 0 and 100.")

        # Lock the cart so two concurrent checkout requests cannot
        # create multiple orders from the same cart.
        cart = Cart.objects.select_for_update().get(
            pk=cart.pk,
            user=user,
        )

        if cart.submited:
            raise ValueError("This cart has already been submitted.")

        cart_items = list(
            cart.items.select_related(
                "stock",
                "stock__product",
            )
        )

        if not cart_items:
            raise ValueError("Cannot create an order from an empty cart.")

        if coupon_application is not None:
            if coupon_application.user_id != user.pk:
                raise ValueError("This coupon application does not belong to the user.")

            if coupon_application.cart_id != cart.pk:
                raise ValueError("This coupon application does not belong to the cart.")

        subtotal = Decimal("0.00")
        order_items = []

        for cart_item in cart_items:
            stock = cart_item.stock
            unit_price = stock.get_final_price

            if unit_price is None:
                raise ValueError(f"Product '{stock.product.title}' has no price.")

            unit_price = Decimal(unit_price).quantize(
                TWOPLACES,
                rounding=ROUND_HALF_UP,
            )

            total_price = (unit_price * cart_item.quantity).quantize(
                TWOPLACES,
                rounding=ROUND_HALF_UP,
            )

            subtotal += total_price

            order_items.append(
                {
                    "cart_item": cart_item,
                    "unit_price": unit_price,
                    "total_price": total_price,
                }
            )

        subtotal = subtotal.quantize(
            TWOPLACES,
            rounding=ROUND_HALF_UP,
        )

        coupon = None
        discount_percent = Decimal("0.00")

        if coupon_application is not None:
            coupon = coupon_application.coupon
            discount_percent = coupon.discount

            if not Decimal("0.00") <= discount_percent <= Decimal("100.00"):
                raise ValueError("Invalid coupon discount.")

        discount_amount = (subtotal * discount_percent / Decimal("100")).quantize(
            TWOPLACES,
            rounding=ROUND_HALF_UP,
        )

        discounted_subtotal = (subtotal - discount_amount).quantize(
            TWOPLACES,
            rounding=ROUND_HALF_UP,
        )

        shipping_amount = shipping_method.price

        if shipping_method.free_shipping:
            threshold = shipping_method.free_shipping_threshold

            if threshold is None or subtotal >= threshold:
                shipping_amount = Decimal("0.00")

        shipping_amount = Decimal(shipping_amount).quantize(
            TWOPLACES,
            rounding=ROUND_HALF_UP,
        )

        tax_amount = (discounted_subtotal * tax_rate / Decimal("100")).quantize(
            TWOPLACES,
            rounding=ROUND_HALF_UP,
        )

        total_amount = (discounted_subtotal + tax_amount + shipping_amount).quantize(
            TWOPLACES,
            rounding=ROUND_HALF_UP,
        )

        order = Order.objects.create(
            user=user,
            cart=cart,
            shipping_address=shipping_address,
            shipping_method=shipping_method,
            subtotal=subtotal,
            discount_amount=discount_amount,
            tax_rate=tax_rate,
            tax_amount=tax_amount,
            shipping_amount=shipping_amount,
            total_amount=total_amount,
            coupon_code=coupon.code if coupon else "",
            coupon_discount_percent=discount_percent,
        )

        OrderItem.objects.bulk_create(
            [
                OrderItem(
                    order=order,
                    stock=data["cart_item"].stock,
                    quantity=data["cart_item"].quantity,
                    unit_price=data["unit_price"],
                    total_price=data["total_price"],
                    product_name=data["cart_item"].stock.product.title,
                    sku=data["cart_item"].stock.sku,
                )
                for data in order_items
            ]
        )

        cart.submited = True
        cart.date_submitted = timezone.now()
        cart.save(
            update_fields=[
                "submited",
                "date_submitted",
            ]
        )

        return order
