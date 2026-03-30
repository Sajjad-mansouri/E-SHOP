from django.urls import path, include
from .views import (RegistrationView, RegistrationConfirmView, RegistrationDoneView,
					ProfileView, UpdateProfileView, DeleteProfileView

	)

app_name = "account"
urlpatterns = [
	path("register/<uidb64>/<token>/", RegistrationConfirmView.as_view(), name="register-confirm"),
	path("", include("django.contrib.auth.urls")),
	path("register/", RegistrationView.as_view(), name="register"),
	path("register/registration_done/", RegistrationDoneView.as_view(), name="registration_done"),

	path("profile/", ProfileView.as_view(), name="profile"),
	path("profile/edit/<int:pk>/", UpdateProfileView.as_view(), name="edit_profile"),
	path("profile/delete/<int:pk>/", DeleteProfileView.as_view(), name="delete_profile"),




]