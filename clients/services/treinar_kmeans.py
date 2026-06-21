from clients.models import Client


def classificar_investidor(cliente):

    score = 0

    # =========================
    # 1. VOLATILIDADE
    # =========================
    if cliente.tolerancia_volatilidade <= 3:
        score -= 2
    elif cliente.tolerancia_volatilidade <= 6:
        score += 0
    else:
        score += 2

    # =========================
    # 2. EXPERIÊNCIA
    # =========================
    if cliente.experiencia_em_investimentos == "Nenhuma":
        score -= 2
    elif cliente.experiencia_em_investimentos == "Iniciante":
        score -= 1
    elif cliente.experiencia_em_investimentos == "Intermediario":
        score += 1
    else:
        score += 2

    # =========================
    # 3. PERDA
    # =========================
    if cliente.aceitacao_perda_percentual <= 5:
        score -= 2
    elif cliente.aceitacao_perda_percentual <= 15:
        score += 0
    else:
        score += 2

    # =========================
    # 4. LIQUIDEZ
    # =========================
    if cliente.liquidez_necessaria in ["Imediata", "Curto_prazo"]:
        score -= 2
    elif cliente.liquidez_necessaria == "Medio_prazo":
        score += 0
    else:
        score += 2

    # =========================
    # 5. OBJETIVO
    # =========================
    if cliente.objetivo_de_vida == "Preservacao":
        score -= 2
    elif cliente.objetivo_de_vida in ["Aposentadoria", "Imovel"]:
        score += 0
    else:
        score += 2

    # =========================
    # CLASSIFICAÇÃO FINAL
    # =========================
    if score <= -3:
        return "Conservador"
    elif score <= 2:
        return "Moderado"
    else:
        return "Agressivo"


def atualizar_investidores():

    clientes = list(Client.objects.all())

    if not clientes:
        return

    for cliente in clientes:
        cliente.tipo_de_investidor = classificar_investidor(cliente)

    Client.objects.bulk_update(clientes, ["tipo_de_investidor"])