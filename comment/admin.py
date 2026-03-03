from django.contrib import admin

from .models import Comment

@admin.register(Comment)
class CommendAdmin(admin.ModelAdmin):
	list_display = ["user", "content_object"]
