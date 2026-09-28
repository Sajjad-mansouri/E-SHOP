from django.urls import path

from . import views

app_name = "landing"

urlpatterns = [
    path("", views.landing_page, name="home"),
    path("message/", views.ContactMessage.as_view(), name="contact_message"),
]
