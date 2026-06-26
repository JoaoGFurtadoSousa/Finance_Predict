from django.core.management.base import BaseCommand
from clients.models import Client
from faker import Faker
from decimal import Decimal
import random

fake = Faker("pt_BR")


def gerar_cliente(perfil: str):
    """
    Gera cliente sintético coerente com o perfil de investidor.
    """

    idade = {
        "Conservador": random.randint(50, 70),
        "Moderado": random.randint(30, 50),
        "Agressivo": random.randint(20, 35),
    }[perfil]

    renda = {
        "Conservador": random.randint(4000, 9000),
        "Moderado": random.randint(7000, 15000),
        "Agressivo": random.randint(12000, 30000),
    }[perfil]

    aporte = round(renda * random.uniform(0.05, 0.25), 2)

    patrimonio = renda * random.randint(12, 120)

    dividas = random.choice([True, False]) if perfil != "Conservador" else random.choice([False, False, True])

    reserva = round(aporte * random.randint(3, 12), 2)

    tolerancia_volatilidade = {
        "Conservador": random.randint(1, 3),
        "Moderado": random.randint(4, 7),
        "Agressivo": random.randint(8, 10),
    }[perfil]

    aceitacao_perda = {
        "Conservador": random.choice([5, 10]),
        "Moderado": random.choice([10, 20]),
        "Agressivo": random.choice([20, 30, 50]),
    }[perfil]

    experiencia = {
        "Conservador": "Nenhuma",
        "Moderado": random.choice(["Iniciante", "Intermediario"]),
        "Agressivo": random.choice(["Intermediario", "Avancado"]),
    }[perfil]

    liquidez = {
        "Conservador": "Imediata",
        "Moderado": "Curto_prazo",
        "Agressivo": random.choice(["Medio_prazo", "Longo_prazo"]),
    }[perfil]

    objetivo = {
        "Conservador": random.choice(["Preservacao", "Aposentadoria"]),
        "Moderado": random.choice(["Aposentadoria", "Imovel", "Viagens"]),
        "Agressivo": "Renda_passiva",
    }[perfil]

    horizonte = {
        "Conservador": random.randint(1, 5),
        "Moderado": random.randint(5, 15),
        "Agressivo": random.randint(10, 30),
    }[perfil]

    return {
        "nome": fake.name(),
        "cpf": "".join(filter(str.isdigit, fake.cpf()))[:11],
        "email": fake.unique.email(),

        "idade": idade,
        "renda_atual": Decimal(str(renda)),
        "aporte_mensal": Decimal(str(aporte)),

        "reserva_de_emergencia": True if reserva > 0 else False,
        "valor_armazenado_reserva_emergencia": Decimal(str(reserva)),

        "possui_dividas": dividas,

        "tolerancia_volatilidade": tolerancia_volatilidade,
        "experiencia_em_investimentos": experiencia,
        "aceitacao_perda_percentual": aceitacao_perda,
        "liquidez_necessaria": liquidez,

        "objetivo_de_vida": objetivo,
        "tempo_estimado_retorno": horizonte,

        "valor_desejado_acumulado": Decimal(
            str(renda * random.randint(20, 200))
        ),

        "preocupacao_atual": random.choice([
            "Preocupacao com a inflacao",
            "Planejamento da aposentadoria",
            "Seguranca financeira da familia",
            "Busca por estabilidade financeira",
        ]),

        "tipo_de_investidor": perfil,
    }


class Command(BaseCommand):
    help = "Popula o banco com clientes sintéticos baseados em perfis de investidor"

    def handle(self, *args, **kwargs):

        self.stdout.write(self.style.WARNING("Gerando dataset de ML..."))

        clientes = []

        # Conservadores
        for _ in range(1800):
            clientes.append(gerar_cliente("Conservador"))

        # Moderados
        for _ in range(1700):
            clientes.append(gerar_cliente("Moderado"))

        # Agressivos
        for _ in range(1500):
            clientes.append(gerar_cliente("Agressivo"))

        objs = [
            Client(**c)
            for c in clientes
        ]

        Client.objects.bulk_create(objs, batch_size=1000)

        self.stdout.write(
            self.style.SUCCESS(
                f"{len(objs)} clientes criados com sucesso!"
            )
        )
