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

        An order can have multiple payment attempts. A pending payment
        is reused only when its Stripe Checkout Session is still open.

        If the previous Checkout Session has expired, the previous
        payment attempt is cancelled and a new payment attempt is created.

        The order total is authoritative and is never recalculated from
        the cart during payment.
        """

        # ===============================================================
        # Phase 1
        # Lock the order and determine the payment attempt.
        #
        # Stripe is never called while the database transaction is
        # holding the order lock.
        # ===============================================================
        with transaction.atomic():
            order = (
                Order.objects.select_for_update()
                .select_related("user")
                .get(pk=order.pk)
            )

            # -----------------------------------------------------------
            # Ownership
            # -----------------------------------------------------------
            if order.user_id != user.pk:
                raise OrderAccessDenied("You do not have access to this order.")

            # -----------------------------------------------------------
            # Order status
            # -----------------------------------------------------------
            if order.status != Order.STATUS_PENDING:
                raise OrderNotPayable("This order is not available for payment.")

            # -----------------------------------------------------------
            # Validate order amount
            # -----------------------------------------------------------
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
            # Never create another payment for an already-paid order.
            # -----------------------------------------------------------
            if order.payments.filter(
                status=Payment.Status.SUCCEEDED,
            ).exists():
                raise OrderAlreadyPaid("This order has already been paid.")

            # -----------------------------------------------------------
            # Find the latest pending payment attempt.
            # -----------------------------------------------------------
            existing_pending = (
                order.payments.filter(status=Payment.Status.PENDING)
                .order_by("-created_at")
                .first()
            )

            # -----------------------------------------------------------
            # If there is an existing pending payment with a Stripe
            # Checkout Session, determine whether that session is still
            # usable.
            #
            # IMPORTANT:
            # Stripe must be queried outside the database transaction.
            # Therefore we only collect the session ID here.
            # -----------------------------------------------------------
            existing_session_id = None

            if existing_pending:
                existing_session_id = existing_pending.stripe_checkout_session_id

        # ===============================================================
        # Phase 2
        # Inspect an existing Stripe Checkout Session.
        #
        # This happens outside the DB transaction so we never hold a
        # database lock while making a network request to Stripe.
        # ===============================================================

        if existing_pending and existing_session_id:
            try:
                session = stripe.checkout.Session.retrieve(
                    existing_session_id,
                )

            except stripe.StripeError as exc:
                logger.warning(
                    "Unable to retrieve Stripe Checkout Session %s "
                    "for payment_id=%s: %s",
                    existing_session_id,
                    existing_pending.id,
                    exc,
                )

                # We cannot safely assume the session is expired.
                # Return the existing payment so the caller does not
                # accidentally create another payment attempt.
                return existing_pending

            if session.status == "complete":
                # The webhook should normally process this state.
                # Do not create another payment attempt.
                raise OrderAlreadyPaid("This order has already been paid.")

            if session.status == "open":
                # The customer can continue the existing Checkout Session.
                return existing_pending

            if session.status == "expired":
                # The existing payment attempt can no longer be used.
                # It will be cancelled and replaced below.
                pass

        elif existing_pending:
            # A pending payment without a Stripe session means the
            # previous Stripe session creation did not complete.
            pass

        # ===============================================================
        # Phase 3
        # Lock the order again and create a new payment attempt if the
        # previous attempt is no longer usable.
        # ===============================================================
        with transaction.atomic():
            order = (
                Order.objects.select_for_update()
                .select_related("user")
                .get(pk=order.pk)
            )

            # -----------------------------------------------------------
            # Re-check ownership and order state after reacquiring the
            # database lock.
            # -----------------------------------------------------------
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
            # Re-check successful payments while holding the lock.
            # -----------------------------------------------------------
            if order.payments.filter(
                status=Payment.Status.SUCCEEDED,
            ).exists():
                raise OrderAlreadyPaid("This order has already been paid.")

            # -----------------------------------------------------------
            # Re-check pending payments.
            #
            # Another request may have created/reused a payment while
            # we were communicating with Stripe.
            # -----------------------------------------------------------
            existing_pending = (
                order.payments.filter(status=Payment.Status.PENDING)
                .order_by("-created_at")
                .first()
            )

            if existing_pending:
                session_id = existing_pending.stripe_checkout_session_id

                if session_id:
                    try:
                        session = stripe.checkout.Session.retrieve(
                            session_id,
                        )

                    except stripe.StripeError as exc:
                        logger.warning(
                            "Unable to retrieve Stripe Checkout Session "
                            "%s for payment_id=%s: %s",
                            session_id,
                            existing_pending.id,
                            exc,
                        )

                        return existing_pending

                    if session.status == "open":
                        return existing_pending

                    if session.status == "complete":
                        raise OrderAlreadyPaid("This order has already been paid.")

                # -------------------------------------------------------
                # The pending payment has no usable Stripe session.
                # Preserve the payment attempt but mark it cancelled.
                # -------------------------------------------------------
                existing_pending.status = Payment.Status.CANCELLED
                existing_pending.error_message = (
                    "Stripe Checkout Session is no longer available."
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
        # Phase 4
        # Create a new Stripe Checkout Session.
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
                                "name": f"Order #{order.order_number}",
                                "description": "E-commerce order payment",
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
        # Phase 5
        # Save Stripe Checkout Session information.
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
