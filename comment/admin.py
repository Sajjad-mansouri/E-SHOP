from django.contrib import admin

from .models import Comment, ReviewReaction


@admin.register(Comment)
class CommendAdmin(admin.ModelAdmin):
    list_display = ["user", "content_object"]


@admin.register(ReviewReaction)
class ReviewReactionAdmin(admin.ModelAdmin):
    list_display = ["user", "review", "like", "unlike"]
