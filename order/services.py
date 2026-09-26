# order/services.py

from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from .models import Order, OrderItem


class OrderCheckoutService:
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
        if cart.submited:
            raise ValueError("This cart has already been submitted.")

        cart_items = list(cart.items.select_related("stock"))

        if not cart_items:
            raise ValueError("Cannot create an order from an empty cart.")

        # -----------------------------
        # Item snapshots
        # -----------------------------

        subtotal = Decimal("0.00")
        order_items = []

        for cart_item in cart_items:
            unit_price = cart_item.stock.get_final_price
            total_price = unit_price * cart_item.quantity

            subtotal += total_price

            order_items.append(
                {
                    "cart_item": cart_item,
                    "unit_price": unit_price,
                    "total_price": total_price,
                }
            )

        # -----------------------------
        # Coupon snapshot
        # -----------------------------

        coupon = None
        discount_percent = Decimal("0.00")

        if coupon_application:
            coupon = coupon_application.coupon
            discount_percent = Decimal(coupon.discount)

        discount_amount = subtotal * discount_percent / Decimal("100")

        discounted_subtotal = subtotal - discount_amount

        # -----------------------------
        # Shipping snapshot
        # -----------------------------

        shipping_amount = shipping_method.price

        if shipping_method.free_shipping:
            threshold = shipping_method.free_shipping_threshold

            if threshold is None or subtotal >= threshold:
                shipping_amount = Decimal("0.00")

        # -----------------------------
        # Tax
        # -----------------------------

        tax_amount = discounted_subtotal * tax_rate / Decimal("100")

        # -----------------------------
        # Final total
        # -----------------------------

        total_amount = discounted_subtotal + tax_amount + shipping_amount

        # -----------------------------
        # Create Order
        # -----------------------------

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
            # Replace these with your actual Address fields.
            shipping_full_name=shipping_address.full_name,
            shipping_address_line_1=shipping_address.address_line_1,
            shipping_address_line_2=shipping_address.address_line_2,
            shipping_city=shipping_address.city,
            shipping_state=shipping_address.state,
            shipping_postal_code=shipping_address.postal_code,
            shipping_country=shipping_address.country,
        )

        # -----------------------------
        # Create OrderItems
        # -----------------------------

        OrderItem.objects.bulk_create(
            [
                OrderItem(
                    order=order,
                    stock=data["cart_item"].stock,
                    quantity=data["cart_item"].quantity,
                    unit_price=data["unit_price"],
                    total_price=data["total_price"],
                    # Replace with your actual product fields.
                    product_name=str(data["cart_item"].stock),
                )
                for data in order_items
            ]
        )

        # -----------------------------
        # Submit cart
        # -----------------------------

        cart.submited = True
        cart.date_submitted = timezone.now()
        cart.save(
            update_fields=[
                "submited",
                "date_submitted",
            ]
        )

        return order
