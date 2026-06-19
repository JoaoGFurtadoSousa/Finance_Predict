from django.db.models.signals import pre_save
from django.dispatch import receiver
from .services.kmeans_classifier import classificar_cliente
from .models import Client


@receiver(pre_save, sender=Client)
def categorizes_the_new_clients_investor_type(sender, instance, **kwargs):
    instance.tipo_de_investidor = classificar_cliente(instance)
    print(instance)

