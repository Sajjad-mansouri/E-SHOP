from django.shortcuts import render,get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
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
		print(form.errors)

	return JsonResponse({"status":"failed"})


@require_POST
def remove_review(request):
	print(request.POST)
	comment_id = request.POST.get('commentId')
	print(comment_id)
	try:
		get_object_or_404(Comment, id=comment_id).delete()
		return JsonResponse({'status':'ok'})
	except:
		return JsonResponse({'status':'failed'})


