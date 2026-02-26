from django.shortcuts import render
from django.views.generic.base import View, TemplateResponseMixin


class HomePageView(TemplateResponseMixin, View):
	template_name = "catalog/list/home.html"
	def get(self, request, *args, **kwargs):
		context = {}
		return self.render_to_response(context)

