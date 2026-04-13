from django.urls import path
from . import views

app_name = "comment"
urlpatterns = [
	path("create_review/", views.create_review, name="create_review"),
	path("update/<int:pk>/", views.CommentUpdateView.as_view(), name="update_review"),
	path("remove_review/", views.remove_review, name="remove_review"),


]	