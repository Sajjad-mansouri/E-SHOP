from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.generic.base import View
from django.views.generic.edit import CreateView, UpdateView

from .forms import CommentForm
from .models import Comment, ReviewReaction


class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        stock_record = form.cleaned_data.pop("stock_record")

        form = form.save(commit=False)
        form.user = self.request.user
        form.content_object = stock_record
        form.save()
        stock_record.save()
        return render(self.request, "comment/comment_item.html", {"comment": form})

    def form_invalid(self, form):
        return HttpResponse("")


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    http_method_names = ["post"]

    def form_valid(self, form):
        self.obj = form.save()
        stock_record = self.obj.content_object

        stock_record.save()

        product_ratings = Comment.objects.filter(
            stockrecord=stock_record, user=self.request.user
        ).aggregate(rating_mean=Avg("rating", default=0))
        return JsonResponse(
            {"status": True, "total_rating": product_ratings["rating_mean"]}
        )

    def form_invalid(self, form):
        return JsonResponse({"status": False})


class ReviewRemoveView(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        comment_id = request.POST.get("commentId")
        try:
            obj = Comment.objects.get(id=comment_id, user=request.user)
            stock_record = obj.content_object
            product_ratings_count = (
                Comment.objects.filter(stockrecord=stock_record).distinct().count()
            )
            rating_counts = product_ratings_count - 1

            obj.delete()

            return JsonResponse({"status": True, "rating_counts": rating_counts})
        except Comment.DoesNotExist:
            return JsonResponse({"status": False})


class ReviewReactionView(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        reaction = request.POST.get("reaction")
        review_id = request.POST.get("review_id")
        if request.user.is_authenticated:
            review = Comment.objects.get(id=int(review_id))
            try:
                review_reaction = ReviewReaction.objects.get(
                    user=request.user, review=review
                )

            except ReviewReaction.DoesNotExist:
                review_reaction = ReviewReaction.objects.create(
                    user=request.user, review=review
                )

            if reaction == "like":
                review_reaction.like = True
                review_reaction.unlike = False

            elif reaction == "unlike":
                review_reaction.unlike = True
                review_reaction.like = False
            review_reaction.save()
            return JsonResponse({"status": True})

        else:
            return JsonResponse({"status": False})
