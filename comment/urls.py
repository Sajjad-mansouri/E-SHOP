from django.urls import path
from . import views

app_name = "comment"
urlpatterns = [
	path("create_review/", views.ReviewCreateView.as_view(), name="create_review"),
	path("update/<int:pk>/", views.CommentUpdateView.as_view(), name="update_review"),
	path("remove_review/", views.ReviewRemoveView.as_view(), name="remove_review"),
	path("review_reaction/", views.ReviewReactionView.as_view(), name="review_reaction"),



]	