from django.contrib import admin

from .models import Comment, ReviewLike

@admin.register(Comment)
class CommendAdmin(admin.ModelAdmin):
	list_display = ["user", "content_object"]


@admin.register(ReviewLike)
class CommendAdmin(admin.ModelAdmin):
	list_display = ["user", "review", "like", "unlike"]