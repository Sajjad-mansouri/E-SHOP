from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

UserModel = get_user_model()

class Comment(models.Model):
	user = models.ForeignKey(
							UserModel, 
							on_delete=models.CASCADE,
							related_name="comments", 
							verbose_name=_("user"))

	parent = models.ForeignKey(
								'self', 
								on_delete=models.CASCADE,
								blank=True,
								null=True,
								verbose_name=_("parent")

								)

	content_type = models.ForeignKey(
									ContentType, 
									on_delete=models.CASCADE,
									verbose_name=_("content type")

									)

	object_id = models.PositiveIntegerField(verbose_name=_("object id"))
	content_object = GenericForeignKey("content_type", "object_id")
	content = models.TextField(verbose_name=_("content"))
	created = models.DateTimeField(auto_now_add=True, verbose_name=_("created"))
	updated = models.DateTimeField(auto_now=True, verbose_name=_("updated"))

	def __str__(self):
		if self.parent:
			return f"commented by {self.user}"
		else:
			return f"reply by {self.user}"

	class Meta:
		ordering = ["-created"]
		verbose_name = _("Comment")
		verbose_name_plural = _("Comments")
