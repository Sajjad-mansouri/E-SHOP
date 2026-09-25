from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Profile, User


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ("user_type",)
    fieldsets = (
        *UserAdmin.fieldsets,
        (
            "Additional Information",
            {
                "fields": ("user_type",),
            },
        ),
    )
    ordering = ("-date_joined",)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass
