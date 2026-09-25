from django.urls import path

from .views import WishListCreateView

app_name = "wishlist"
urlpatterns = [
    path("add_remove/", WishListCreateView.as_view(), name="wishlist"),
]
