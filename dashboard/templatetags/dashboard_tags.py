from django import template


register = template.Library()

@register.simple_tag(takes_context=True)
def is_active_link(context, link):
	request = context["request"]
	print(request.path, link)
	if request.path.startswith(f"/dashboard/{link}"):
		return "active"


@register.simple_tag
def get_expire_class(hours):
	print(hours)
	if hours <= 24:
		return "expiry-critical"
	elif hours <= 72:
		return "expiry-warning"

@register.simple_tag
def is_expiring(hours):
	print('is_expiring')
	if hours <= 72:
		return True
	else:
		return False