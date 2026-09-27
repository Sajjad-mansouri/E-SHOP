import uuid

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        SUCCEEDED = "succeeded", "Succeeded"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"
        PARTIALLY_REFUNDED = "partially_refunded", "Partially Refunded"
        CANCELLED = "cancelled", "Cancelled"

    class Type(models.TextChoices):
        ONE_TIME = "one_time", "One-time Payment"
        SUBSCRIPTION = "subscription", "Subscription"
        INSTALLMENT = "installment", "Installment"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    order = models.ForeignKey(
        "order.Order",
        on_delete=models.PROTECT,
        related_name="payments",
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    currency = models.CharField(
        max_length=3,
        default="USD",
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING,
    )
    payment_type = models.CharField(
        max_length=20,
        choices=Type.choices,
        default=Type.ONE_TIME,
    )
    stripe_checkout_session_id = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
    )
    stripe_checkout_url = models.URLField(max_length=500, blank=True, null=True)
    stripe_payment_intent_id = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
    )
    stripe_event_id = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
    )
    stripe_customer_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    refunded_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    description = models.TextField(
        blank=True,
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
    )

    error_message = models.TextField(
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["order", "status"],
            ),
            models.Index(
                fields=["stripe_customer_id"],
            ),
        ]

    def __str__(self):
        return f"Payment {self.id} - {self.amount} {self.currency} - {self.status}"
