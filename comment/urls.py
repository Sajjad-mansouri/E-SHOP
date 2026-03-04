from django.urls import path
from . import views


urlpatterns = [
	path("create_review/", views.create_review, name="create_review")
]	