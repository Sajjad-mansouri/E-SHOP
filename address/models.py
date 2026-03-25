from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

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
	full_name = models.CharField(_("Full name"), max_length=255, blank=True)
	address_type = models.CharField(_("Address Type"), choices=ADDRESS_TYPE, max_length=20)
	phone_number = models.CharField(_("Phone Number"), max_length=15)
	city = models.CharField(_("City"), max_length=255, blank=True)
	province = models.CharField(_("Province/State"), max_length=255, blank=True)
	country = models.CharField(_("country"), blank=True)
	postcode = models.CharField(_("Post/Zip-code"), max_length=64, blank=True)
	line1 = models.CharField(_("First line of address"), max_length=255, help_text=_("Street address, P.O. box, company name"))
	line2 = models.CharField(_("Second line of address"), max_length=255, blank=True, help_text=_("Apartment, suite, unit, building, floor, etc."))


	def __str__(self):
		return f"{self.first_name} {self.last_name}"

	class Meta:
		verbose_name = _("Address")
		verbose_name_plural = _("Addresses")