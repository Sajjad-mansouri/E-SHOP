from django.shortcuts import render
from django.views.generic.base import View, TemplateResponseMixin
from catalog.models import Category


class HomePageView(TemplateResponseMixin, View):
	template_name = "catalog/list/home.html"
	def get(self, request, *args, **kwargs):
		categories = Category.objects.all()
		root_categories = []
		for category in categories:
			if category.is_root():
				root_categories.append(category)
				category.get_children()
		print(root_categories)

		context = {'categories':root_categories}
		return self.render_to_response(context)

