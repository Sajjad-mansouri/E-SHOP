from django.contrib import admin

from .models import (
    Contact,
    EmailInbox,
    FeatureItem,
    HighlightEdpoint,
    SiteFeature,
    SiteHighlight,
    SocialLink,
    Statistics,
)

admin.site.register(EmailInbox)
admin.site.register(SiteFeature)

admin.site.register(SiteHighlight)
admin.site.register(HighlightEdpoint)
admin.site.register(Contact)
admin.site.register(SocialLink)
admin.site.register(Statistics)


@admin.register(FeatureItem)
class FeatureItemAdmin(admin.ModelAdmin):
    list_display = ["title", "feature"]
    list_filter = ["feature"]
