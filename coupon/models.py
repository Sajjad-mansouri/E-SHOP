from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

class Coupon(models.Model):
	code = models.CharField(_("code"), max_length=50, unique=True)
	description = models.TextField(_("Description"), blank=True)
	valid_from = models.DateTimeField(_("valid from"))
	valid_to = models.DateTimeField(_("valid to"))
	discount = models.IntegerField(_("discount"), validators=[MinValueValidator(0),MaxValueValidator(100)])
	active = models.BooleanField(_("active"))

	SINGLE_USE, MULTI_USE, ONCE_PER_CUSTOMER = (
		"Single use",
		"Multi-use",
		"Once per customer",
	)
	USAGE_CHOICES = (
		(SINGLE_USE, _("Can be used once by one customer")),
		(MULTI_USE, _("Can be used multiple times by multiple customers")),
		(ONCE_PER_CUSTOMER, _("Can only be used once per customer")),
	)
	usage = models.CharField(
		_("Usage"), max_length=128, choices=USAGE_CHOICES, default=MULTI_USE
	)
	num_orders = models.PositiveIntegerField(_("Times on orders"), default=0)
	date_created = models.DateTimeField(_("date created"), auto_now_add=True, db_index=True)
	date_updated = models.DateTimeField(_("date updated"), auto_now_add=True)


	class Meta:
		verbose_name = _("Coupon")
		verbose_name_plural = _("Coupons")


	def __str__(self):
		return self.code

	def is_active(self, test_datetime=None):

		datetime = timezone.now()
		return self.valid_from <= datetime <= self.valid_to



	def clean(self):
		if (
			self.valid_from
			and self.valid_to
			and (self.valid_from > self.valid_to)
		):
			raise exceptions.ValidationError(
				_("End date should be later than start date")
			)