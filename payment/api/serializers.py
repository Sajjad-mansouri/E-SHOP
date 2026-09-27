from rest_framework import serializers

from payment.models import Payment


class CheckoutSessionResponseSerializer(serializers.ModelSerializer):
    checkout_url = serializers.URLField(source="stripe_checkout_url", read_only=True)

    class Meta:
        model = Payment
        fields = ["id", "checkout_url", "amount", "currency"]
        read_only_fields = fields
