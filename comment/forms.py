from django import forms
from .models import Comment
from stock.models import StockRecord

class CommentForm(forms.ModelForm):
	stock_record = forms.ModelChoiceField(queryset=StockRecord.objects.all(), widget=forms.HiddenInput)
	class Meta:
		model = Comment
		fields = ["content"]