from django.db import models
from django.utils.translation import gettext_lazy as _
# Create your models here.
class Address(models.Model):

    first_name = models.CharField(_("First name"), max_length=255, blank=True)
    last_name = models.CharField(_("Last name"), max_length=255, blank=True)
    city = models.CharField(_("City"), max_length=255, blank=True)
    province = models.CharField(_("Province/State"), max_length=255, blank=True)
    country = models.CharField(_("country"), blank=True)
    postcode = models.CharField(_("Post/Zip-code"), max_length=64, blank=True)
    address = models.TextField(_("address"))

    def __str__(self):
    	return f"{self.first_name} {self.last_name}"

    class Meta:
    	verbose_name = _("Address")
    	verbose_name_plural = _("Addresses")