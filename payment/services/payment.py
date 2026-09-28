import logging

from django.db import transaction
from django.utils import timezone

from order.models import Order
from payment.models import Payment
from stock.models import StockRecord

logger = logging.getLogger(__name__)


class PaymentService:
    @classmethod
    @transaction.atomic
    def complete_payment(
        cls,
        *,
        payment: Payment,
        stripe_payment_intent_id: str | None,
    ) -> None:
        """
        Mark a payment as successful and finalize the related order.

        Inventory is deducted only after Stripe has confirmed payment.
        The operation is atomic and idempotent.
        """

        payment = (
            Payment.objects.select_for_update()
            .select_related("order")
            .get(pk=payment.pk)
        )

        # -----------------------------------------------------------
        # Idempotency
        # -----------------------------------------------------------
        if payment.status == Payment.Status.SUCCEEDED:
            return

        order = Order.objects.select_for_update().get(pk=payment.order_id)

        order_items = list(order.items.select_related("stock"))

        # -----------------------------------------------------------
        # Lock all stock records before checking availability.
        # -----------------------------------------------------------
        stock_ids = {item.stock_id for item in order_items if item.stock_id is not None}

        stocks = {
            stock.id: stock
            for stock in (
                StockRecord.objects.select_for_update().filter(id__in=stock_ids)
            )
        }

        # -----------------------------------------------------------
        # Validate inventory.
        # -----------------------------------------------------------
        for item in order_items:
            if item.stock_id is None:
                raise ValueError(f"Order item {item.pk} has no stock record.")

            stock = stocks.get(item.stock_id)

            if stock is None:
                raise ValueError(f"Stock record {item.stock_id} does not exist.")

            if stock.num_in_stock is None:
                continue

            if stock.num_in_stock < item.quantity:
                raise ValueError(f"Insufficient stock for stock record {stock.pk}.")

        # -----------------------------------------------------------
        # Deduct inventory.
        # -----------------------------------------------------------
        for item in order_items:
            stock = stocks[item.stock_id]

            if stock.num_in_stock is not None:
                stock.num_in_stock -= item.quantity

            stock.sold += item.quantity

            stock.save(
                update_fields=[
                    "num_in_stock",
                    "sold",
                    "date_updated",
                ]
            )

        # -----------------------------------------------------------
        # Mark payment as successful.
        # -----------------------------------------------------------
        payment.status = Payment.Status.SUCCEEDED
        payment.stripe_payment_intent_id = stripe_payment_intent_id
        payment.paid_at = timezone.now()

        payment.save(
            update_fields=[
                "status",
                "stripe_payment_intent_id",
                "paid_at",
                "updated_at",
            ]
        )

        # -----------------------------------------------------------
        # Move the order to processing.
        # -----------------------------------------------------------
        if order.status == Order.STATUS_PENDING:
            order.status = Order.STATUS_PROCESSING

            order.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

        logger.info(
            "Payment %s completed successfully for order %s",
            payment.id,
            order.id,
        )
