from django import template


register = template.Library()

@register.simple_tag(takes_context=True)
def is_active_link(context, link):
	request = context["request"]
	print(request.path, link)
	if link in request.path:
		return "active"