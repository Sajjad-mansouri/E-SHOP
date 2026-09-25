from django import forms

from stock.models import StockRecord

from .models import Comment


class CommentForm(forms.ModelForm):
    stock_record = forms.ModelChoiceField(
        queryset=StockRecord.objects.all(), widget=forms.HiddenInput
    )

    class Meta:
        model = Comment
        fields = ["content", "rating"]
