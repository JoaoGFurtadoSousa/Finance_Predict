"""Configurações centralizadas e sobrescrevíveis via Django settings."""

from django.conf import settings


def guardrail_setting(name, default):
    return getattr(settings, name, default)


MAX_INPUT_LENGTH = lambda: guardrail_setting("GUARDRAIL_MAX_INPUT_LENGTH", 5_000)
MAX_SINGLE_ASSET_PERCENT = lambda: guardrail_setting(
    "MAX_SINGLE_ASSET_PERCENT", 40
)
MAX_CRYPTO_PERCENT = lambda: guardrail_setting("MAX_CRYPTO_PERCENT", 15)
MAX_LEVERAGE = lambda: guardrail_setting("MAX_LEVERAGE", 1.0)


PROFILE_RULES = {
    "Conservador": {
        "allowed": (
            "tesouro selic",
            "cdb",
            "lci",
            "lca",
            "fundo conservador",
            "renda fixa",
        ),
        "blocked": (
            "opções",
            "opcoes",
            "day trade",
            "alavancagem",
            "cripto",
            "bitcoin",
            "ethereum",
        ),
    },
    "Moderado": {
        "allowed": (),
        "blocked": ("day trade", "alavancagem máxima", "alavancagem maxima"),
    },
    "Agressivo": {"allowed": (), "blocked": ()},
}


def profile_rules():
    return guardrail_setting("INVESTMENT_PROFILE_RULES", PROFILE_RULES)
