import logging
from decimal import ROUND_HALF_UP, Decimal

import stripe
from django.conf import settings
from django.db import transaction

from order.models import Order
from payment.exceptions import (
    OrderAccessDenied,
    OrderAlreadyPaid,
    OrderAmountInvalid,
    OrderNotPayable,
    StripeSessionCreationFailed,
)
from payment.models import Payment

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY

TWOPLACES = Decimal("0.01")


class CheckoutService:
    @classmethod
    def create_checkout_session(
        cls,
        *,
        order: Order,
        user,
    ) -> Payment:
        """
        Create or reuse a Stripe Checkout Session for an order.

        An order may have multiple payment attempts. A failed or cancelled
        payment is preserved and a new Payment is created for a subsequent
        checkout attempt.

        The order total is authoritative and is never recalculated from
        the cart during payment.
        """

        # ===============================================================
        # Phase 1
        # Lock the order and determine the payment attempt.
        #
        # Stripe must not be called while holding the database lock.
        # ===============================================================
        with transaction.atomic():
            order = (
                Order.objects.select_for_update()
                .select_related("user")
                .get(pk=order.pk)
            )

            if order.user_id != user.pk:
                raise OrderAccessDenied("You do not have access to this order.")

            if order.status != Order.STATUS_PENDING:
                raise OrderNotPayable("This order is not available for payment.")

            if order.total_amount is None:
                raise OrderAmountInvalid(
                    "This order does not have a valid total amount."
                )

            amount = Decimal(order.total_amount).quantize(
                TWOPLACES,
                rounding=ROUND_HALF_UP,
            )

            if amount <= Decimal("0.00"):
                raise OrderAmountInvalid("This order does not require payment.")

            # -----------------------------------------------------------
            # An order that already has a successful payment must never
            # create another checkout session.
            # -----------------------------------------------------------
            if order.payments.filter(
                status=Payment.Status.SUCCEEDED,
            ).exists():
                raise OrderAlreadyPaid("This order has already been paid.")

            # -----------------------------------------------------------
            # Reuse an existing pending payment when it already has a
            # Stripe Checkout URL.
            #
            # Do not cancel a pending payment merely because it is older
            # than an arbitrary number of minutes. Stripe Checkout
            # sessions can remain valid much longer.
            # -----------------------------------------------------------
            existing_pending = (
                order.payments.filter(status=Payment.Status.PENDING)
                .order_by("-created_at")
                .first()
            )

            if existing_pending and existing_pending.stripe_checkout_url:
                return existing_pending

            # -----------------------------------------------------------
            # If a pending Payment exists but Stripe session creation
            # previously failed, mark that attempt as failed before
            # creating a new payment attempt.
            # -----------------------------------------------------------
            if existing_pending:
                existing_pending.status = Payment.Status.FAILED
                existing_pending.error_message = (
                    "Previous checkout attempt did not create a "
                    "Stripe Checkout Session."
                )
                existing_pending.save(
                    update_fields=[
                        "status",
                        "error_message",
                        "updated_at",
                    ]
                )

            currency = getattr(
                settings,
                "STRIPE_CURRENCY",
                "USD",
            ).upper()

            payment = Payment.objects.create(
                order=order,
                amount=amount,
                currency=currency,
                status=Payment.Status.PENDING,
                payment_type=Payment.Type.ONE_TIME,
                description=f"Payment for order {order.order_number}",
                metadata={
                    "order_id": str(order.id),
                    "order_number": str(order.order_number),
                    "user_id": str(user.pk),
                },
            )

        # ===============================================================
        # Phase 2
        # Create the Stripe Checkout Session.
        #
        # The database transaction has already committed.
        # ===============================================================

        try:
            unit_amount = int(
                (payment.amount * Decimal("100")).quantize(
                    Decimal("1"),
                    rounding=ROUND_HALF_UP,
                )
            )

            if unit_amount <= 0:
                raise OrderAmountInvalid("The payment amount is invalid.")

            session = stripe.checkout.Session.create(
                mode="payment",
                line_items=[
                    {
                        "price_data": {
                            "currency": payment.currency.lower(),
                            "product_data": {
                                "name": (f"Order #{order.order_number}"),
                                "description": ("E-commerce order payment"),
                            },
                            "unit_amount": unit_amount,
                        },
                        "quantity": 1,
                    }
                ],
                metadata={
                    "payment_id": str(payment.id),
                    "order_id": str(order.id),
                    "order_number": str(order.order_number),
                    "user_id": str(user.pk),
                },
                client_reference_id=str(payment.id),
                customer_email=(user.email if getattr(user, "email", None) else None),
                success_url=(
                    f"{settings.FRONTEND_URL}"
                    "/payment/success"
                    "?session_id={CHECKOUT_SESSION_ID}"
                    f"&order_number={order.order_number}"
                ),
                cancel_url=(
                    f"{settings.FRONTEND_URL}"
                    "/payment/cancel"
                    f"?order_id={order.id}"
                    f"&order_number={order.order_number}"
                ),
            )

        except stripe.StripeError as exc:
            logger.exception(
                "Stripe Checkout Session creation failed "
                "for payment_id=%s, order_id=%s",
                payment.id,
                order.id,
            )

            payment.status = Payment.Status.FAILED
            payment.error_message = str(exc)
            payment.save(
                update_fields=[
                    "status",
                    "error_message",
                    "updated_at",
                ]
            )

            raise StripeSessionCreationFailed(
                "Unable to create the payment session."
            ) from exc

        # ===============================================================
        # Phase 3
        # Save Stripe session information.
        # ===============================================================
        payment.stripe_checkout_session_id = session.id
        payment.stripe_checkout_url = session.url
        payment.save(
            update_fields=[
                "stripe_checkout_session_id",
                "stripe_checkout_url",
                "updated_at",
            ]
        )

        return payment
