from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

from .models import Contact, SiteFeature, SiteHighlight, Statistics
from .serializers import EmailInboxSerializer
from .tasks import send_email_task


@require_http_methods(["GET"])
def landing_page(request):
    context = {
        "features": SiteFeature.objects.prefetch_related("items").all(),
        "highlights": SiteHighlight.objects.prefetch_related("endpoints").all(),
        "statistics": Statistics.objects.first(),
        "contact": Contact.objects.prefetch_related("social_links").first(),
    }
    return render(request, "landing/landing.html", context)


def get_current_site_address(request):
    current_site = get_current_site(request)
    site_name = current_site.name
    protocol = "https" if request.is_secure() else "http"
    site_address = f"{protocol}://{current_site.domain}"
    return site_name, site_address


def message_feedback(request, name, user_email, message):
    site_name, site_address = get_current_site_address(request)
    kwargs = {
        "site_name": site_name,
        "site_address": site_address,
        "name": name,
        "email": user_email,
        "message": message,
    }
    if settings.HOST_ASYNC_ABILITY:
        send_email_task.delay(**kwargs)
    else:
        send_email_task(**kwargs)


class ContactMessage(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = EmailInboxSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        message_feedback(self.request, instance.name, instance.email, instance.message)
