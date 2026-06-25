from django.db import models


PERFIL_CHOICES = [
    ('Conservador', 'Conservador'),
    ('Moderado', 'Moderado'),
    ('Agressivo', 'Agressivo')
]


class PerfilInvestidor(models.Model):
    nome = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.nome



class ClasseAtivo(models.Model):
    nome = models.CharField(max_length=100)
    perfil = models.ForeignKey(PerfilInvestidor, on_delete=models.CASCADE, related_name="classes")
    risco = models.IntegerField()
    
    def __str__(self):
        return self.nome


class Investimento(models.Model):    
    nome = models.CharField(max_length=100, unique= True)
    ticker = models.CharField(max_length=20, blank=True, null=True)
    tipo_investimento = models.ForeignKey(ClasseAtivo, on_delete=models.CASCADE)
    rentabilidade_anual = models.DecimalField(max_digits=6, decimal_places=2, help_text="Percentual médio anual")
    volatilidade = models.DecimalField(max_digits=6, decimal_places=2, help_text="Percentual")
    liquidez_dias = models.IntegerField()
    risco = models.IntegerField(help_text="1 a 5")
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome


class Cotacao(models.Model):
    investimento = models.ForeignKey(
        Investimento,
        on_delete=models.CASCADE
    )

    preco = models.DecimalField(max_digits= 10, decimal_places= 2)
    data = models.DateTimeField()