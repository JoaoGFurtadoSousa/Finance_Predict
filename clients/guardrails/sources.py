"""Exige fontes não vazias e com formato minimamente válido."""

from urllib.parse import urlparse

from .audit import log_guardrail
from .exceptions import GuardrailViolation


class SourceValidationGuardrail:
    name = "SOURCE_VALIDATION"

    def validate(self, recommendation):
        items = self._items(recommendation)
        if not items:
            self._block()
        for item in items:
            sources = item.get("sources") if isinstance(item, dict) else None
            if not sources or not any(self._valid(source) for source in sources):
                self._block()
        return recommendation

    @staticmethod
    def _items(recommendation):
        if not isinstance(recommendation, dict):
            return []
        items = recommendation.get("recommendations", recommendation.get("assets"))
        if items is None and recommendation.get("asset"):
            items = [recommendation]
        return [item for item in (items or []) if isinstance(item, dict)]

    @staticmethod
    def _valid(source):
        if isinstance(source, dict):
            source = source.get("url", source.get("source", ""))
        if not isinstance(source, str) or not source.strip():
            return False
        parsed = urlparse(source.strip())
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)

    def _block(self):
        reason = "MISSING_OR_INVALID_SOURCE"
        log_guardrail(self.name, reason, "UNVERIFIED_SOURCE")
        raise GuardrailViolation(
            self.name,
            reason,
            "Toda recomendação deve incluir pelo menos uma fonte válida.",
        )
