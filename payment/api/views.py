import stripe
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from order.models import Order
from payment.api.serializers import CheckoutSessionResponseSerializer
from payment.exceptions import (
    OrderAccessDenied,
    OrderAlreadyPaid,
    OrderAmountInvalid,
    OrderNotPayable,
    StripeSessionCreationFailed,
)
from payment.services.checkout import CheckoutService
from payment.services.webhook import (
    handle_checkout_session_completed,
)


class CreateCheckoutSessionApiView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        order = get_object_or_404(
            Order,
            id=order_id,
            user=request.user,
        )

        try:
            payment = CheckoutService.create_checkout_session(
                order=order,
                user=request.user,
            )

        except OrderAccessDenied as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_403_FORBIDDEN,
            )

        except OrderNotPayable as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except OrderAlreadyPaid as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_409_CONFLICT,
            )

        except OrderAmountInvalid as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except StripeSessionCreationFailed as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        serializer = CheckoutSessionResponseSerializer(payment)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookApiView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        payload = request.body
        sig_header = request.META.get(
            "HTTP_STRIPE_SIGNATURE",
            "",
        )

        try:
            event = stripe.Webhook.construct_event(
                payload,
                sig_header,
                settings.STRIPE_WEBHOOK_SECRET,
            )
        except ValueError:
            return HttpResponse(status=400)
        except stripe.SignatureVerificationError:
            return HttpResponse(status=400)

        event_type = event["type"]

        if event_type == "checkout.session.completed":
            handle_checkout_session_completed(
                event["data"]["object"],
            )

        return HttpResponse(status=200)
