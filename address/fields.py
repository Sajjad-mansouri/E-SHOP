import re

from django.core import exceptions
from django.db import models

PHONE_REGEX = {
    "US": r"^\+?1?[2-9]\d{9}$",
    "CA": r"^\+?1?[2-9]\d{9}$",
    "IR": r"^(\+98|0)?9\d{9}$",
    "AU": r"^(\+61|0)?4\d{8}$",
    "UK": r"^(\+44|0)?7\d{9}$",
    "GER": r"^(\+49|0)?1[5-7]\d{8,9}$",
}


class PhoneNumberField(models.CharField):
    """
    Custom Django model field for storing phone numbers.
    """

    def to_python(self, value):
        value = super().to_python(value)
        if value is None:
            return value
        return self.normalize_phone(value)

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        return self.to_python(value)

    def normalize_phone(self, phone: str) -> str:
        # keep digits and +
        phone = phone.strip()
        phone = re.sub(r"[^\d+]", "", phone)
        if phone == "":
            raise exceptions.ValidationError(
                "Enter a valid phone number.",
                code="invalid_phone_number",
                params={"value": phone},
            )

        # convert 00 international prefix to +
        if phone.startswith("00"):
            phone = "+" + phone[2:]

        return phone

    def validate(self, value, model_instance):
        super().validate(value, model_instance)
        country = model_instance.country
        pattern = PHONE_REGEX.get(country)
        if pattern and not re.match(pattern, value):
            raise exceptions.ValidationError(f"Invalid {country} phone number format.")
