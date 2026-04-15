from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .models import Offer
from stock.models import StockRecord



@receiver(pre_delete, sender=Offer, dispatch_uid="my_unique_identifier")
def my_callback(sender, signal, instance,  **kwargs):
	instance.offer_type.offer_range.get_products.update(offer_discount=0)
