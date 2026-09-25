from django import forms

from .models import Address


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            "full_name",
            "address_type",
            "phone_number",
            "city",
            "province",
            "country",
            "postcode",
            "line1",
            "line2",
            "is_default_address",
        ]
        widgets = {
            "full_name": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Your full name..."}
            ),
            "phone_number": forms.TextInput(attrs={"class": "form-input"}),
            "line1": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Street address,..."}
            ),
            "line2": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "Apartment, suite, unit, etc",
                }
            ),
            "city": forms.TextInput(attrs={"class": "form-input"}),
            "province": forms.TextInput(attrs={"class": "form-input"}),
            "postcode": forms.TextInput(attrs={"class": "form-input"}),
            "country": forms.Select(attrs={"class": "form-input"}),
            "address_type": forms.Select(attrs={"class": "form-input"}),
            "is_default_address": forms.CheckboxInput(attrs={"class": "form-checkbox"}),
        }
