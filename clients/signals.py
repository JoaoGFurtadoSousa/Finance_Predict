from django.db.models.signals import pre_save
from django.dispatch import receiver
from .services.random_forest import InvestorPredictor
from .models import Client


@receiver(pre_save, sender=Client)
def categorizes_the_new_clients_investor_type(sender, instance, **kwargs):
    predict = InvestorPredictor()
    instance.tipo_de_investidor = predict.predict(instance)
   
