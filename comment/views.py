import json
from django.shortcuts import render,get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.generic.edit import UpdateView
from django.db.models import Avg
from .forms import CommentForm
from .models import Comment



@require_POST
def create_review(request):
	form = CommentForm(request.POST)

	if form.is_valid():
		stock_record = form.cleaned_data.pop("stock_record")
		
		form = form.save(commit=False)
		form.user = request.user
		form.content_object = stock_record
		form.save()
		return render(request, "comment/comment_item.html", {'comment':form})

	else:
		pass

	return JsonResponse({"status":False})

class CommentUpdateView(UpdateView):
	model = Comment
	form_class = CommentForm

	def form_valid(self, form):
		self.obj = form.save()
		stock_record = self.obj.content_object
		product_ratings = Comment.objects.filter(stockrecord=stock_record).aggregate(rating_mean=Avg("rating", default=0))
		return JsonResponse({"status":True, "total_rating":product_ratings["rating_mean"]})

	def form_invalid(self, form):
		return JsonResponse({"status":False})


@require_POST
def remove_review(request):

	comment_id = request.POST.get('commentId')
	print("comment_id", comment_id)
	try:
		obj = Comment.objects.get(id=comment_id)
		stock_record = obj.content_object
		product_ratings_count = Comment.objects.filter(stockrecord=stock_record).distinct().count()
		rating_counts = product_ratings_count - 1
		obj.delete()

		return JsonResponse({'status':'ok', "rating_counts":rating_counts})
	except:
		return JsonResponse({'status':'failed'})


