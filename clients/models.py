from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


OBJETIVO_DE_VIDA = (
    ('Aposentadoria', 'Aposentadoria'),
    ('Imovel', 'Imovel'),
    ('Viagens', 'Viagens'),
    ('Preservacao', 'Preservacao'),
    ('Renda_passiva', 'Renda Passiva'),
)

EXPERIENCIA_EM_INVESTIMENTOS = (
    ('Nenhuma', 'Nenhuma'),
    ('Iniciante', 'Iniciante'),
    ('Intermediario', 'Intermediario'),
    ('Avancado', 'Avancado'),
)

LIQUIDEZ_NECESSARIA = (
    ('Imediata', 'Imediata'),
    ('Curto_prazo', 'Curto prazo'),
    ('Medio_prazo', 'Medio prazo'),
    ('Longo_prazo', 'Longo prazo')
)

TIPOS_DE_INVESTIDOR = (
    ('Conservador', 'Conservador'),
    ('Moderado', 'Moderado'),
    ('Agressivo', 'Agressivo')
)


class Client(models.Model):
    nome = models.CharField(max_length=150)
    cpf = models.CharField(max_length=12)
    email = models.EmailField(unique=True)
    idade = models.IntegerField(validators= [ MinValueValidator(18)])
    renda_atual = models.DecimalField(max_digits= 15, decimal_places= 2)
    aporte_mensal = models.DecimalField(max_digits= 15, decimal_places= 2)
    reserva_de_emergencia = models.BooleanField(default=False)
    valor_armazenado_reserva_emergencia = models.DecimalField(max_digits= 15, decimal_places= 2)
    possui_dividas = models.BooleanField(default= True)
    tolerancia_volatilidade = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)], default= 3)
    experiencia_em_investimentos = models.CharField(choices= EXPERIENCIA_EM_INVESTIMENTOS, default='Iniciante')
    aceitacao_perda_percentual = models.IntegerField(default= 5)
    liquidez_necessaria = models.CharField(choices= LIQUIDEZ_NECESSARIA, default='Imediata')
    objetivo_de_vida = models.CharField(choices=OBJETIVO_DE_VIDA)
    tempo_estimado_retorno = models.IntegerField()
    valor_desejado_acumulado = models.DecimalField(max_digits= 15, decimal_places= 2)
    preocupacao_atual = models.CharField(max_length= 500)
    tipo_de_investidor = models.CharField(choices= TIPOS_DE_INVESTIDOR, blank=True, null= True)
    perfil_sintetico = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.nome
