from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from .fields import PhoneNumberField

UserModel = get_user_model()
# Create your models here.
class Address(models.Model):
	user = models.ForeignKey(
		UserModel, 
		on_delete=models.SET_NULL, 
		null=True, blank=True, 
		related_name="addresses", 
		verbose_name=_("user")
		)
	ADDRESS_TYPE=[
		("Home", "Home"),
		("Work", "Work"),
		("Other", "Other"),


	]
	COUNTRIES=[
		("IR", "Iran"),
		("US", "United States"),
		("CA", "Canada"),
		("UK", "United Kingdom"),
		("AU", "Australia"),
		("GER", "Germany"),

	]
	full_name = models.CharField(_("Full name"), max_length=255)
	country = models.CharField(_("country"),choices=COUNTRIES)
	phone_number = PhoneNumberField(_("Phone Number"), max_length=20)
	address_type = models.CharField(_("Address Type"), choices=ADDRESS_TYPE, max_length=20, blank=True)
	city = models.CharField(_("City"), max_length=255)
	province = models.CharField(_("Province/State"), max_length=255)
	postcode = models.CharField(_("Post/Zip-code"), max_length=64)
	line1 = models.CharField(_("First line of address"), max_length=255, help_text=_("Street address, P.O. box, company name"))
	line2 = models.CharField(_("Second line of address"), max_length=255, blank=True, help_text=_("Apartment, suite, unit, building, floor, etc."))
	is_default_address = models.BooleanField(_("Default"), default=False)

	def __str__(self):
		return f"{self.full_name}"

	class Meta:
		verbose_name = _("Address")
		verbose_name_plural = _("Addresses")