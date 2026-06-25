"""Validação final fail-closed antes de entregar a recomendação."""

from .audit import log_guardrail
from .exceptions import GuardrailViolation


REQUIRED_CHECKS = (
    "profile_match",
    "compliance_ok",
    "has_sources",
    "no_guarantees",
    "no_excessive_concentration",
    "no_hallucination",
)


class OutputGuardrail:
    name = "OUTPUT"

    def validate(self, recommendation, checklist):
        failed = [name for name in REQUIRED_CHECKS if checklist.get(name) is not True]
        if failed:
            reason = "OUTPUT_CHECKLIST_FAILED"
            log_guardrail(self.name, reason, "UNSAFE_OUTPUT")
            raise GuardrailViolation(
                self.name,
                reason,
                "A resposta não passou pela validação final de segurança.",
                {"failed_checks": failed},
            )
        return recommendation
