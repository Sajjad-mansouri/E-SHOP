import logging
from datetime import timedelta
from decimal import Decimal

import stripe
from django.conf import settings
from django.db import transaction
from django.utils import timezone

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


class CheckoutService:
    @staticmethod
    def create_checkout_session(*, order: Order, user) -> Payment:
        """
        Create or reuse a pending Payment and create a Stripe Checkout Session.

        The order and payment validation happens inside a short database
        transaction. Stripe is called only after the transaction commits.
        """

        # ---------------------------------------------------------------
        # Phase 1:
        # Lock the order and validate payment state.
        # ---------------------------------------------------------------
        with transaction.atomic():
            order = (
                Order.objects.select_for_update()
                .select_related("user")
                .get(pk=order.pk)
            )

            if order.user_id != user.id:
                raise OrderAccessDenied("You do not have access to this order.")

            if order.status not in {
                Order.STATUS_PENDING,
            }:
                raise OrderNotPayable("This order is not available for payment.")

            if order.total_amount is None:
                raise OrderAmountInvalid(
                    "This order does not have a valid total amount."
                )

            if order.total_amount <= Decimal("0.00"):
                raise OrderAmountInvalid("This order does not require payment.")

            if order.payments.filter(
                status=Payment.Status.SUCCEEDED,
            ).exists():
                raise OrderAlreadyPaid("This order has already been paid.")

            # -----------------------------------------------------------
            # Reuse a recent pending payment when possible.
            # -----------------------------------------------------------
            existing_pending = (
                order.payments.filter(
                    status=Payment.Status.PENDING,
                )
                .order_by("-created_at")
                .first()
            )

            if existing_pending:
                payment_age = timezone.now() - existing_pending.created_at

                if payment_age > timedelta(minutes=1):
                    existing_pending.status = Payment.Status.CANCELLED

                    existing_pending.save(
                        update_fields=[
                            "status",
                            "updated_at",
                        ]
                    )

                elif existing_pending.stripe_checkout_url:
                    return existing_pending

            currency = getattr(
                order,
                "currency",
                "USD",
            ).upper()

            payment = Payment.objects.create(
                order=order,
                amount=order.total_amount,
                currency=currency,
                status=Payment.Status.PENDING,
                payment_type=Payment.Type.ONE_TIME,
                description=f"Payment for order {order.order_number}",
                metadata={
                    "order_id": str(order.id),
                    "order_number": str(order.order_number),
                    "user_id": str(user.id),
                },
            )

        # ---------------------------------------------------------------
        # Phase 2:
        # Create Stripe Checkout Session.
        #
        # IMPORTANT:
        # The DB transaction has already committed.
        # ---------------------------------------------------------------
        try:
            unit_amount = int((payment.amount * Decimal("100")).quantize(Decimal("1")))

            items = list(
                order.items.select_related(
                    "stock",
                    "stock__product",
                )
            )

            line_items = []

            for item in items:
                line_items.append(
                    {
                        "price_data": {
                            "currency": payment.currency.lower(),
                            "product_data": {
                                "name": item.product_name,
                            },
                            "unit_amount": unit_amount,
                        },
                        "quantity": item.quantity,
                    }
                )

            session = stripe.checkout.Session.create(
                mode="payment",
                line_items=line_items,
                metadata={
                    "payment_id": str(payment.id),
                    "order_id": str(order.id),
                    "order_number": str(order.order_number),
                    "user_id": str(user.id),
                },
                customer_email=getattr(
                    user,
                    "email",
                    None,
                ),
                client_reference_id=str(payment.id),
                success_url=(
                    f"{settings.FRONTEND_URL}"
                    "/payment/success"
                    "?session_id={CHECKOUT_SESSION_ID}"
                ),
                cancel_url=(f"{settings.FRONTEND_URL}/payment/cancel"),
            )

        except stripe.StripeError as exc:
            logger.exception(
                "Stripe checkout session creation failed for payment_id=%s",
                payment.id,
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

        # ---------------------------------------------------------------
        # Phase 3:
        # Save Stripe Checkout Session information.
        # ---------------------------------------------------------------
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
