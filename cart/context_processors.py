from .models import Cart


def count_cart(request):
	try:
		cart = Cart.objects.get(user=request.user, submited=False)
		return {"len_cart":cart.items.count()}
	except Cart.DoesNotExist:
		return {"len_cart":0}