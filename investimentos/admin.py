from django.contrib import admin
from .models import ClasseAtivo, PerfilInvestidor, Cotacao, Investimento


@admin.register(PerfilInvestidor)
class ClasseAtivoAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome', )


@admin.register(ClasseAtivo)
class ClasseAtivoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'perfil', 'risco',)
    search_fields = ('nome', )

@admin.register(Investimento)
class ClasseAtivoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ticker', 'tipo_investimento', 'rentabilidade_anual', 'volatilidade', 'liquidez_dias', 'risco', 'criado_em',)
    search_fields = ('nome', )


@admin.register(Cotacao)
class ClasseAtivoAdmin(admin.ModelAdmin):
    list_display = ('investimento', 'preco', 'data',)
    search_fields = ('investimento', )