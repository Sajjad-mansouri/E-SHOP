from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .forms import CommentForm



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
