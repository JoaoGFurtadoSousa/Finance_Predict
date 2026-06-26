"""Ponto único para executar geradores de recomendação com guardrails."""

from clients.guardrails import InvestmentGuardrails


class GuardedInvestmentRecommendationService:
    """
    Envolve qualquer agente/cadeia sem conhecer sua implementação.

    ``generator`` deve receber o prompt já anonimizado e o contexto de
    suitability, retornando a estrutura de recomendação com ativos, fontes e
    justificativas.
    """

    def __init__(self, generator, guardrails=None):
        self.generator = generator
        self.guardrails = guardrails or InvestmentGuardrails()

    def recommend(self, user_input, context):
        safe_input = self.guardrails.process_input(user_input)
        safe_context = self.guardrails.process_input(
            context,
            pii_excluded_fields={"tipo_de_investidor", "profile", "risk_profile"},
        )
        self.guardrails.validate_suitability(safe_context)

        recommendation = self.generator(safe_input, safe_context)
        profile = (
            safe_context.get("tipo_de_investidor")
            or safe_context.get("profile")
            or safe_context.get("risk_profile")
        )
        return self.guardrails.process_output(recommendation, profile)
