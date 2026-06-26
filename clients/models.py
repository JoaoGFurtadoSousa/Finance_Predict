from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import (
    MaxValueValidator,
    MinLengthValidator,
    MinValueValidator,
)
from django.db import models

from core.guardrails.sanitizers import sanitize_email, sanitize_text
from core.guardrails.security import validate_safe_text
from core.guardrails.validators import normalize_cpf, validate_cpf, validate_name


OBJETIVO_DE_VIDA = (
    ("Aposentadoria", "Aposentadoria"),
    ("Imovel", "Imovel"),
    ("Viagens", "Viagens"),
    ("Preservacao", "Preservacao"),
    ("Renda_passiva", "Renda Passiva"),
)

EXPERIENCIA_EM_INVESTIMENTOS = (
    ("Nenhuma", "Nenhuma"),
    ("Iniciante", "Iniciante"),
    ("Intermediario", "Intermediario"),
    ("Avancado", "Avancado"),
)

LIQUIDEZ_NECESSARIA = (
    ("Imediata", "Imediata"),
    ("Curto_prazo", "Curto prazo"),
    ("Medio_prazo", "Medio prazo"),
    ("Longo_prazo", "Longo prazo"),
)

TIPOS_DE_INVESTIDOR = (
    ("Conservador", "Conservador"),
    ("Moderado", "Moderado"),
    ("Agressivo", "Agressivo"),
)


class ValidatingManager(models.Manager):
    def bulk_create(self, objs, **kwargs):
        for obj in objs:
            obj.normalize_fields()
            obj.full_clean(validate_unique=False)
        return super().bulk_create(objs, **kwargs)


class Client(models.Model):
    nome = models.CharField(max_length=150, validators=[validate_name])
    cpf = models.CharField(max_length=11, validators=[validate_cpf])
    email = models.EmailField(unique=True)
    idade = models.IntegerField(
        validators=[MinValueValidator(18), MaxValueValidator(100)]
    )
    renda_atual = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    aporte_mensal = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
    )
    reserva_de_emergencia = models.BooleanField(default=False)
    valor_armazenado_reserva_emergencia = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
    )
    possui_dividas = models.BooleanField(default=True)
    tolerancia_volatilidade = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)], default=3
    )
    experiencia_em_investimentos = models.CharField(
        max_length=20,
        choices=EXPERIENCIA_EM_INVESTIMENTOS,
        default="Iniciante",
    )
    aceitacao_perda_percentual = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=5,
    )
    liquidez_necessaria = models.CharField(
        max_length=20,
        choices=LIQUIDEZ_NECESSARIA,
        default="Imediata",
    )
    objetivo_de_vida = models.CharField(max_length=20, choices=OBJETIVO_DE_VIDA)
    tempo_estimado_retorno = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    valor_desejado_acumulado = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    preocupacao_atual = models.CharField(
        max_length=500, validators=[MinLengthValidator(10)]
    )
    tipo_de_investidor = models.CharField(
        max_length=20, choices=TIPOS_DE_INVESTIDOR, blank=True, null=True
    )
    perfil_sintetico = models.CharField(max_length=20, null=True, blank=True)
