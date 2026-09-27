class PaymentError(Exception):
    """Base exception for payment domain errors."""


class OrderAccessDenied(PaymentError):
    """Raised when the user does not own the order."""


class OrderNotPayable(PaymentError):
    """Raised when the order is not in a payable state."""


class OrderAlreadyPaid(PaymentError):
    """Raised when the order already has a successful payment."""


class OrderAmountInvalid(PaymentError):
    """Raised when the order total is not valid for payment."""


class StripeSessionCreationFailed(PaymentError):
    """Raised when Stripe fails to create a Checkout Session."""
