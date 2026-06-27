from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Client


@receiver(post_save, sender=Client)
def categorizes_the_new_clients_investor_type(sender, instance, created, **kwargs):
    """
    Classifica automaticamente o perfil do investidor após a criação do cliente.
    """

    # Executa somente na criação
    if not created:
        return

    score = 0

    # --------------------------
    # Experiência
    # --------------------------

    experiencia_score = {
        "Nenhuma": 0,
        "Iniciante": 1,
        "Intermediario": 2,
        "Avancado": 3,
    }

    score += experiencia_score.get(instance.experiencia_em_investimentos, 0)

    # --------------------------
    # Liquidez
    # Quanto maior o prazo aceito,
    # maior o perfil de risco.
    # --------------------------

    liquidez_score = {
        "Imediata": 0,
        "Curto_prazo": 1,
        "Medio_prazo": 2,
        "Longo_prazo": 3,
    }

    score += liquidez_score.get(instance.liquidez_necessaria, 0)

    # --------------------------
    # Volatilidade (1-10)
    # --------------------------

    if instance.tolerancia_volatilidade <= 3:
        score += 0
    elif instance.tolerancia_volatilidade <= 6:
        score += 2
    else:
        score += 3

    # --------------------------
    # Perda aceitável (0-100%)
    # --------------------------

    if instance.aceitacao_perda_percentual <= 10:
        score += 0
    elif instance.aceitacao_perda_percentual <= 30:
        score += 2
    else:
        score += 3

    # --------------------------
    # Perfil final
    # Score máximo = 12
    # --------------------------

    if score <= 3:
        perfil = "Conservador"

    elif score <= 7:
        perfil = "Moderado"

    else:
        perfil = "Agressivo"

    # Atualiza diretamente no banco
    sender.objects.filter(pk=instance.pk).update(
        tipo_de_investidor=perfil
    )

    print(f"Perfil classificado automaticamente: {perfil}")