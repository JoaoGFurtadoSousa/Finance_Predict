from django.contrib import admin
from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('nome', 'idade', 'email', 'idade', 'renda_atual', 'renda_atual', 'aporte_mensal', 'reserva_de_emergencia', 'valor_armazenado_reserva_emergencia', )
    list_filter = ('reserva_de_emergencia', )
