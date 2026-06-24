"""Garante compatibilidade entre produtos sugeridos e perfil do ML."""

from .audit import log_guardrail
from .config import profile_rules
from .exceptions import GuardrailViolation
from .utils import normalize_text


class ProfileMatchingGuardrail:
    name = "PROFILE_MATCHING"

    def validate(self, recommendation, profile):
        rules = profile_rules().get(str(profile), {})
        text = normalize_text(recommendation)
        blocked = [
            product
            for product in rules.get("blocked", ())
            if normalize_text(product) in text
        ]
        if blocked:
            reason = "PROFILE_MISMATCH"
            log_guardrail(self.name, reason, "UNSUITABLE_RECOMMENDATION")
            raise GuardrailViolation(
                self.name,
                reason,
                "A recomendação não é compatível com o perfil do investidor.",
                {"profile": profile, "blocked_products": blocked},
            )
        return recommendation
