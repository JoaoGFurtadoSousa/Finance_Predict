"""Exige justificativa/evidência explícita para cada ativo recomendado."""

from .audit import log_guardrail
from .exceptions import GuardrailViolation
from .sources import SourceValidationGuardrail


EVIDENCE_FIELDS = ("justification", "evidence", "fundamentals", "fundamento", "rationale")


class HallucinationGuardrail:
    name = "HALLUCINATION"

    def validate(self, recommendation):
        items = SourceValidationGuardrail._items(recommendation)
        for item in items:
            if not any(item.get(field) for field in EVIDENCE_FIELDS):
                reason = "MISSING_EVIDENCE"
                log_guardrail(self.name, reason, "UNSUPPORTED_RECOMMENDATION")
                raise GuardrailViolation(
                    self.name,
                    reason,
                    "A recomendação não possui justificativa ou fundamento.",
                    {"asset": item.get("asset", item.get("name", "não informado"))},
                )
        return recommendation
