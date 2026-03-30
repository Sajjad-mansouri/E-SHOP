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
	user_type = models.CharField(_("Type"), choices=USER_TYPES, max_length=10, default="customer")

	USERNAME_FIELD = "email"
	REQUIRED_FIELDS = ["username"]