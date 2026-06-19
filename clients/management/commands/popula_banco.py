from django.core.management.base import BaseCommand
from clients.models import Client

from faker import Faker
from decimal import Decimal
import numpy as np
import random

fake = Faker("pt_BR")

OBJETIVOS = [
    "Aposentadoria",
    "Imovel",
    "Viagens",
    "Renda_passiva"
]

PREOCUPACOES = [
    "Familia",
    "Saude",
    "Inflacao",
    "Aposentadoria",
    "Estabilidade Financeira"
]


def gerar_cliente(
    idade_media,
    idade_std,
    renda_media,
    renda_std,
    horizonte_media,
    horizonte_std
):
    idade = max(
        18,
        int(
            np.random.normal(
                idade_media,
                idade_std
            )
        )
    )

    renda = round(
        max(
            1500,
            np.random.normal(
                renda_media,
                renda_std
            )
        ),
        2
    )

    percentual_aporte = random.uniform(
        0.05,
        0.25
    )

    aporte = round(
        renda * percentual_aporte,
        2
    )

    possui_reserva = random.choice(
        [True, False]
    )

    valor_reserva = (
        round(
            aporte * random.randint(3, 12),
            2
        )
        if possui_reserva
        else 0
    )

    return {
        "nome": fake.name(),
        "cpf": ''.join(
            filter(str.isdigit, fake.cpf())
        )[:11],
        "email": fake.unique.email(),
        "idade": idade,
        "renda_atual": Decimal(str(renda)),
        "aporte_mensal": Decimal(str(aporte)),
        "reserva_de_emergencia": possui_reserva,
        "valor_armazenado_reserva_emergencia": Decimal(
            str(valor_reserva)
        ),
        "possui_dividas": random.choice(
            [True, False]
        ),
        "objetivo_de_vida": random.choice(
            OBJETIVOS
        ),
        "tempo_estimado_retorno": max(
            1,
            int(
                np.random.normal(
                    horizonte_media,
                    horizonte_std
                )
            )
        ),
        "valor_desejado_acumulado": Decimal(
            str(
                round(
                    renda * random.randint(20, 250),
                    2
                )
            )
        ),
        "preocupacao_atual": random.choice(
            PREOCUPACOES
        ),
        "tipo_de_investidor": None
    }


class Command(BaseCommand):

    help = "Popula o banco com clientes sintéticos"

    def handle(self, *args, **kwargs):

        self.stdout.write(
            self.style.WARNING(
                "Gerando clientes sintéticos..."
            )
        )

        clientes = []

        # Conservadores
        for _ in range(1800):
            clientes.append(
                gerar_cliente(
                    idade_media=58,
                    idade_std=7,
                    renda_media=6000,
                    renda_std=1500,
                    horizonte_media=5,
                    horizonte_std=2
                )
            )

        # Moderados
        for _ in range(1700):
            clientes.append(
                gerar_cliente(
                    idade_media=38,
                    idade_std=8,
                    renda_media=8500,
                    renda_std=2500,
                    horizonte_media=10,
                    horizonte_std=3
                )
            )

        # Agressivos
        for _ in range(1500):
            clientes.append(
                gerar_cliente(
                    idade_media=27,
                    idade_std=5,
                    renda_media=15000,
                    renda_std=4000,
                    horizonte_media=20,
                    horizonte_std=5
                )
            )

        objetos = [
            Client(
                nome=c["nome"],
                cpf=c["cpf"],
                email=c["email"],
                idade=c["idade"],
                renda_atual=c["renda_atual"],
                aporte_mensal=c["aporte_mensal"],
                reserva_de_emergencia=c["reserva_de_emergencia"],
                valor_armazenado_reserva_emergencia=c["valor_armazenado_reserva_emergencia"],
                possui_dividas=c["possui_dividas"],
                objetivo_de_vida=c["objetivo_de_vida"],
                tempo_estimado_retorno=c["tempo_estimado_retorno"],
                valor_desejado_acumulado=c["valor_desejado_acumulado"],
                preocupacao_atual=c["preocupacao_atual"],
                tipo_de_investidor=None
            )
            for c in clientes
        ]

        Client.objects.bulk_create(
            objetos,
            batch_size=1000
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"{len(objetos)} clientes criados com sucesso!"
            )
        )