"""Confere os dados mínimos antes de produzir uma recomendação."""

from .audit import log_guardrail
from .exceptions import GuardrailViolation


FIELD_ALIASES = {
    "perfil de risco": (
        "risk_profile",
        "profile",
        "tipo_de_investidor",
        "tolerancia_volatilidade",
    ),
    "objetivo financeiro": ("financial_goal", "objective", "objetivo_de_vida"),
    "horizonte de investimento": (
        "investment_horizon",
        "horizon",
        "tempo_estimado_retorno",
    ),
    "valor disponível para investir": (
        "available_amount",
        "amount",
        "aporte_mensal",
    ),
}


class SuitabilityGuardrail:
    name = "SUITABILITY"

    def validate(self, context):
        missing = []
        for label, aliases in FIELD_ALIASES.items():
            if not any(context.get(alias) not in (None, "") for alias in aliases):
                missing.append(label)

        if missing:
            reason = "MISSING_SUITABILITY_DATA"
            log_guardrail(self.name, reason, "MISSING_DATA")
            raise GuardrailViolation(
                self.name,
                reason,
                "Não é possível gerar uma recomendação sem os dados mínimos.",
                {"missing_fields": missing},
            )
        return context
