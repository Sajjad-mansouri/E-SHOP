import logging

from django.db import transaction
from django.utils import timezone

from order.models import Order
from payment.models import Payment

logger = logging.getLogger(__name__)


@transaction.atomic
def handle_checkout_session_completed(session: dict) -> None:
    session = session.to_dict()

    metadata = session.get("metadata") or {}

    payment_id = metadata.get("payment_id")

    if not payment_id:
        logger.error("checkout.session.completed missing payment_id in metadata")
        return

    try:
        payment = (
            Payment.objects.select_for_update()
            .select_related("order")
            .get(id=payment_id)
        )
    except Payment.DoesNotExist:
        logger.error(
            "Payment %s not found for completed session",
            payment_id,
        )
        return

    # ---------------------------------------------------------------
    # Idempotency
    # ---------------------------------------------------------------
    if payment.status == Payment.Status.SUCCEEDED:
        return

    # ---------------------------------------------------------------
    # Verify that this Stripe session belongs to this Payment.
    # ---------------------------------------------------------------
    session_id = session.get("id")

    if (
        payment.stripe_checkout_session_id
        and payment.stripe_checkout_session_id != session_id
    ):
        logger.error(
            "Stripe session mismatch for payment %s",
            payment.id,
        )
        return

    # ---------------------------------------------------------------
    # Verify the Stripe payment status.
    # ---------------------------------------------------------------
    if session.get("payment_status") != "paid":
        logger.warning(
            "Checkout session %s completed without paid status",
            session_id,
        )
        return

    # ---------------------------------------------------------------
    # Update Payment
    # ---------------------------------------------------------------
    payment.status = Payment.Status.SUCCEEDED
    payment.stripe_payment_intent_id = session.get("payment_intent")
    payment.paid_at = timezone.now()

    payment.save(
        update_fields=[
            "status",
            "stripe_payment_intent_id",
            "paid_at",
            "updated_at",
        ]
    )

    # ---------------------------------------------------------------
    # Update Order
    # ---------------------------------------------------------------
    order = payment.order

    if order.status == Order.STATUS_PENDING:
        order.status = Order.STATUS_PROCESSING
        order.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )
