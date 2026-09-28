import logging

from payment.models import Payment
from payment.services.payment import PaymentService

logger = logging.getLogger(__name__)


def handle_checkout_session_completed(session: dict) -> None:
    session = session.to_dict()

    metadata = session.get("metadata") or {}
    payment_id = metadata.get("payment_id")

    if not payment_id:
        logger.error("checkout.session.completed missing payment_id in metadata")
        return

    try:
        payment = Payment.objects.select_related("order").get(id=payment_id)
    except Payment.DoesNotExist:
        logger.error(
            "Payment %s not found for completed session",
            payment_id,
        )
        return

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

    if session.get("payment_status") != "paid":
        logger.warning(
            "Checkout session %s completed without paid status",
            session_id,
        )
        return

    try:
        PaymentService.complete_payment(
            payment=payment,
            stripe_payment_intent_id=session.get("payment_intent"),
        )
    except ValueError:
        logger.exception(
            "Unable to complete payment %s",
            payment.id,
        )
