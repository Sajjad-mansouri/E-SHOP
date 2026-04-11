from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


class User(AbstractUser):
	USER_TYPES = [
		("seller", "Seller"),
		("customer", "Customer")
	]
	email = models.EmailField(_("email address"), blank=True, unique=True)
	user_type = models.CharField(_("Type"), choices=USER_TYPES, max_length=10, default="customer")

	USERNAME_FIELD = "email"
	REQUIRED_FIELDS = ["username"]

	class Meta(AbstractUser.Meta):
		ordering = ["-date_joined"]


class Profile(models.Model):
	STATUS=[
	("normal", "Normal"),
	("vip", "VIP")
	]
	user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_("user"))
	profile_image = models.ImageField(_("Profile Image"), upload_to="users")
	birth_day = models.DateTimeField(_("Birth Day"), null=True, blank=True)
	status = models.CharField(_("status"), choices=STATUS, max_length=6, default="normal")
	

	def __str__(self):
		return f'"{self.user.get_full_name()}" profile'


	class Meta:
		verbose_name = _("Profile")
		verbose_name_plural = _("Profiles")
