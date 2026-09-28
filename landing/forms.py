from django import forms
from django.utils.translation import gettext_lazy as _

from .models import EmailInbox


class ContactForm(forms.ModelForm):
    class Meta:
        model = EmailInbox
        fields = ["name", "email", "subject", "message"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": _("Your name"),
                    "autocomplete": "name",
                    "required": True,
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "placeholder": _("you@example.com"),
                    "autocomplete": "email",
                    "required": True,
                }
            ),
            "subject": forms.TextInput(attrs={"placeholder": _("Subject (optional)")}),
            "message": forms.Textarea(
                attrs={
                    "placeholder": _(
                        "Tell me about your project, question, or feedback..."
                    ),
                    "rows": 6,
                    "required": True,
                }
            ),
        }

    def clean_name(self):
        name = self.cleaned_data.get("name", "").strip()
        if len(name) < 2:
            raise forms.ValidationError(_("Please enter your name."))
        return name

    def clean_message(self):
        message = self.cleaned_data.get("message", "").strip()
        if len(message) < 10:
            raise forms.ValidationError(_("Message is too short."))
        return message
