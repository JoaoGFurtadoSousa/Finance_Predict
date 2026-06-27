import re
from decimal import Decimal, InvalidOperation

from investimentos.models import Investimento


PROFILE_ALLOWED_RISKS = {
    "Conservador": {1, 2},
    "Moderado": {2, 3},
    "Agressivo": {3, 4, 5},
}

FIELD_PATTERN = re.compile(
    r"^[\-\*\u2022\s]*?(Nome do investimento|Investimento|Ativo|Valor recomendado(?: para investir)?|Valor(?: para investir)?|Motivo(?: da escolha)?|Justificativa)\s*:?\s*(.*)$",
    re.IGNORECASE,
)
SUMMARY_PATTERN = re.compile(
    r"^[\-\*\u2022\s]*?Resumo da estrat(?:e|ae)gia\s*:?\s*$",
    re.IGNORECASE,
)
PORTFOLIO_PATTERN = re.compile(
    r"^[\-\*\u2022\s]*?Carteira recomendada\s*:?\s*$",
    re.IGNORECASE,
)
TOTAL_PATTERN = re.compile(
    r"^[\-\*\u2022\s]*?Total investido\s*:?\s*(.*)$",
    re.IGNORECASE,
)
MONEY_PATTERN = re.compile(r"(?:R\$\s*)?([\d\.,]+)")


def parse_recommendation_text(texto_carteira):
    lines = str(texto_carteira or "").replace("\r\n", "\n").split("\n")
    resumo_lines = []
    investments = []
    current = {"nome": "", "valor": "", "motivo": ""}
    current_field = None
    in_summary = False
    collecting_investments = False

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        if SUMMARY_PATTERN.match(line):
            in_summary = True
            collecting_investments = False
            current_field = None
            continue

        if PORTFOLIO_PATTERN.match(line):
            in_summary = False
            collecting_investments = True
            current_field = None
            continue

        if TOTAL_PATTERN.match(line):
            _commit_investment(investments, current)
            current = {"nome": "", "valor": "", "motivo": ""}
            current_field = None
            collecting_investments = False
            continue

        field_match = FIELD_PATTERN.match(line)
        if field_match:
            label, value = field_match.groups()
            normalized_label = _normalize_label(label)
            if normalized_label == "nome":
                _commit_investment(investments, current)
                current = {"nome": "", "valor": "", "motivo": ""}
            current_field = normalized_label
            current[current_field] = _clean_field_value(value)
            collecting_investments = True
            in_summary = False
            continue

        if in_summary:
            resumo_lines.append(line)
            continue

        if collecting_investments and current_field:
            current[current_field] = " ".join(
                part
                for part in (current[current_field], _clean_field_value(line))
                if part
            )

    _commit_investment(investments, current)
    return {"resumo": "\n".join(resumo_lines).strip(), "investimentos": investments}


def audit_recommendation(cliente, texto_carteira):
    parsed = parse_recommendation_text(texto_carteira)
    inconsistencies = []
    total_recommended = Decimal("0.00")
    allowed_risks = PROFILE_ALLOWED_RISKS.get(cliente.tipo_de_investidor, set())

    for investment_data in parsed["investimentos"]:
        nome = investment_data["nome"]
        valor = _parse_money(investment_data["valor"])
        investimento = Investimento.objects.filter(nome__iexact=nome).select_related(
            "tipo_investimento__perfil"
        ).first()

        if investimento is None:
            inconsistencies.append(
                f'O investimento "{nome}" nao existe no banco de dados.'
            )
            continue

        if investimento.risco not in allowed_risks:
            inconsistencies.append(
                f"O investimento {investimento.nome} possui risco incompativel com o perfil {cliente.tipo_de_investidor}."
            )

        perfil_do_investimento = getattr(
            investimento.tipo_investimento.perfil, "nome", None
        )
        if perfil_do_investimento != cliente.tipo_de_investidor:
            inconsistencies.append(
                f"Foi recomendado um investimento incompativel com o perfil {cliente.tipo_de_investidor}."
            )

        if valor is None:
            continue

        total_recommended += valor
        if cliente.aporte_mensal and cliente.aporte_mensal > 0:
            percentage = (valor / cliente.aporte_mensal) * Decimal("100")
            if percentage > Decimal("50"):
                inconsistencies.append(
                    "Concentracao excessiva detectada.\n\n"
                    f"{investimento.nome} representa {_format_percentage(percentage)} do aporte mensal."
                )

    expected_total = cliente.aporte_mensal or Decimal("0.00")
    if abs(total_recommended - expected_total) > Decimal("0.01"):
        inconsistencies.append(
            "Total recomendado: "
            f"{_format_money(total_recommended)}\n\n"
            f"Total esperado: {_format_money(expected_total)}"
        )

    approved = not inconsistencies
    return {
        "status": "approved" if approved else "rejected",
        "inconsistencies": inconsistencies,
        "message": _build_audit_message(inconsistencies),
    }


def audited_recommendation_text(cliente, texto_carteira):
    audit_result = audit_recommendation(cliente, texto_carteira)
    if audit_result["status"] == "approved":
        return texto_carteira
    return f"{texto_carteira}\n\n{audit_result['message']}"


def _normalize_label(label):
    label = label.lower()
    if label.startswith(("nome do investimento", "investimento", "ativo")):
        return "nome"
    if label.startswith("valor"):
        return "valor"
    return "motivo"


def _commit_investment(investments, current):
    if current["nome"] or current["valor"] or current["motivo"]:
        investments.append(
            {
                "nome": current["nome"].strip(),
                "valor": current["valor"].strip(),
                "motivo": current["motivo"].strip(),
            }
        )


def _parse_money(value):
    if value in (None, ""):
        return None

    cleaned = str(value).strip()
    match = MONEY_PATTERN.search(cleaned)
    normalized = match.group(1) if match else cleaned
    normalized = re.sub(r"[^\d,\.]", "", normalized)

    if not normalized:
        return None

    if "," in normalized:
        normalized = normalized.replace(".", "").replace(",", ".")
    elif normalized.count(".") > 1:
        parts = normalized.split(".")
        normalized = "".join(parts[:-1]) + "." + parts[-1]

    try:
        return Decimal(normalized)
    except (InvalidOperation, TypeError):
        return None


def _format_money(value):
    quantized = Decimal(value).quantize(Decimal("0.01"))
    integer, decimal = f"{quantized:.2f}".split(".")
    grouped = []
    while integer:
        grouped.append(integer[-3:])
        integer = integer[:-3]
    return f"R$ {'.'.join(reversed(grouped))},{decimal}"


def _format_percentage(value):
    quantized = Decimal(value).quantize(Decimal("0.01"))
    text = f"{quantized:.2f}".rstrip("0").rstrip(".")
    return f"{text}%"


def _build_audit_message(inconsistencies):
    if not inconsistencies:
        return (
            "Auditoria concluida.\n\n"
            "Nenhuma inconsistência encontrada.\n\n"
            "Todas as regras de negocio foram respeitadas."
        )
    return "ERRO DE AUDITORIA\n\n" + "\n\n".join(inconsistencies)


def _clean_field_value(value):
    return str(value).strip().strip("-*• ").strip()
