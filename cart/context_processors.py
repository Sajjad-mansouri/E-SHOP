from .models import Cart


def count_cart(request):
	if request.user.is_authenticated:
		try:
			cart = Cart.objects.get(user=request.user, submited=False)
			return {"len_cart":cart.items.count()}
		except Cart.DoesNotExist:
			return {"len_cart":0}
	else:
		return {"len_cart":0}