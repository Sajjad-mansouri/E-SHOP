from django.urls import path, include
from .views import (RegistrationView, RegistrationConfirmView, RegistrationDoneView,
					ProfileView, UpdateProfileView, DeleteProfileView

	)
from . import views

app_name = "account"
urlpatterns = [
	path("register/<uidb64>/<token>/", RegistrationConfirmView.as_view(), name="register-confirm"),
	# path("", include("django.contrib.auth.urls")),
	path("register/", RegistrationView.as_view(), name="register"),
	path("register/registration_done/", RegistrationDoneView.as_view(), name="registration_done"),

	path("profile/", ProfileView.as_view(), name="profile"),
	path("profile/edit/<int:pk>/", UpdateProfileView.as_view(), name="edit_profile"),
	path("profile/delete/<int:pk>/", DeleteProfileView.as_view(), name="delete_profile"),

	path("password_change/", views.PasswordChangeView.as_view(), name="password_change"),

	path("order_history/", views.OrderHistoryView.as_view(), name="order_history"),
	path("order/<int:pk>/", views.OrderDetailView.as_view(), name="order_detail"),
	path("addresses/", views.AddressBookView.as_view(), name="addresses"),
	path("wishlist/", views.WishlistView.as_view(), name="wishlist"),








]