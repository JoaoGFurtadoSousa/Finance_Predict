from django.db.models.signals import post_save
from django.dispatch import receiver

from .services.random_forest import InvestorPredictor
from .models import Client


@receiver(post_save, sender=Client)
def categorizes_the_new_clients_investor_type(sender, instance, created, **kwargs):

    # só classifica se ainda não existe valor manual
    if instance.tipo_de_investidor:
        return

    predictor = InvestorPredictor()

    predicted = predictor.predict(instance)

    sender.objects.filter(pk=instance.pk).update(
        tipo_de_investidor=predicted
    )

    print(f'Classificação automática: {predicted}')