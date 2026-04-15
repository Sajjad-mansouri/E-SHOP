from django.urls import path, include
from . import views

app_name = "account"
urlpatterns = [
	path("login/", views.LoginView.as_view(), name="login"),
	path("logout/", views.LogoutView.as_view(), name="logout"),

	path("register/<uidb64>/<token>/", views.RegistrationConfirmView.as_view(), name="register-confirm"),
	path("register/", views.RegistrationView.as_view(), name="register"),
	path("register/registration_done/", views.RegistrationDoneView.as_view(), name="registration_done"),

	path("password_reset/", views.PasswordResetView.as_view(), name="password_reset"),
    path(
        "password_reset/done/",
        views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),


	path("profile/", views.ProfileView.as_view(), name="profile"),
	path("profile/edit/<int:pk>/", views.UpdateProfileView.as_view(), name="edit_profile"),
	path("profile/delete/<int:pk>/", views.DeleteProfileView.as_view(), name="delete_profile"),
	path("profile/password_change/", views.PasswordChangeView.as_view(), name="password_change"),


	path("profile/order_history/", views.OrderHistoryView.as_view(), name="order_history"),
	path("profile/order/<int:pk>/", views.OrderDetailView.as_view(), name="order_detail"),
	path("profile/addresses/", views.AddressBookView.as_view(), name="addresses"),
	path("profile/wishlist/", views.WishlistView.as_view(), name="wishlist"),
	path("profile/wishlist/remove/", views.WishlistDeleteView.as_view(), name="wishlist_remove"),









]