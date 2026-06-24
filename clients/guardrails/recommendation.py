"""Impede concentração, cripto e alavancagem acima dos limites."""

import re

from . import config
from .audit import log_guardrail
from .exceptions import GuardrailViolation
from .utils import find_percentage, normalize_text


DANGEROUS_PATTERNS = (
    r"\binvista tudo\b",
    r"\bvenda (?:todos|todas) (?:os|as) seus\b",
    r"\balavancagem maxima\b",
    r"\b100\s*%\s*(?:em|de)\s*cripto",
)


class RecommendationGuardrail:
    name = "RECOMMENDATION"

    def validate(self, recommendation):
        text = self._as_text(recommendation)
        normalized = normalize_text(text)
        if any(re.search(pattern, normalized) for pattern in DANGEROUS_PATTERNS):
            self._block("DANGEROUS_RECOMMENDATION")

        for asset in self._assets(recommendation):
            allocation = self._number(asset.get("percentage", asset.get("allocation")))
            name = normalize_text(asset.get("asset", asset.get("name", "")))
            if allocation is not None and allocation > config.MAX_SINGLE_ASSET_PERCENT():
                self._block("EXCESSIVE_SINGLE_ASSET_CONCENTRATION")
            if (
                allocation is not None
                and any(term in name for term in ("cripto", "bitcoin", "ethereum"))
                and allocation > config.MAX_CRYPTO_PERCENT()
            ):
                self._block("EXCESSIVE_CRYPTO_CONCENTRATION")

        crypto = find_percentage(text, ("cripto", "bitcoin", "ethereum"))
        if crypto is not None and crypto > config.MAX_CRYPTO_PERCENT():
            self._block("EXCESSIVE_CRYPTO_CONCENTRATION")

        leverage = self._number(
            recommendation.get("leverage") if isinstance(recommendation, dict) else None
        )
        if leverage is None:
            match = re.search(r"alavancagem[^\d]{0,20}(\d+(?:[.,]\d+)?)\s*x", normalized)
            leverage = self._number(match.group(1)) if match else None
        if leverage is not None and leverage > config.MAX_LEVERAGE():
            self._block("EXCESSIVE_LEVERAGE")
        return recommendation

    def _block(self, reason):
        log_guardrail(self.name, reason, "DANGEROUS_RECOMMENDATION")
        raise GuardrailViolation(
            self.name, reason, "A recomendação ultrapassa os limites de segurança."
        )

    @staticmethod
    def _as_text(value):
        return str(value)

    @staticmethod
    def _assets(value):
        if not isinstance(value, dict):
            return []
        assets = value.get("recommendations", value.get("assets", []))
        if not assets and value.get("asset"):
            assets = [value]
        return [asset for asset in assets if isinstance(asset, dict)]

    @staticmethod
    def _number(value):
        if value in (None, ""):
            return None
        try:
            return float(str(value).replace("%", "").replace(",", "."))
        except (TypeError, ValueError):
            return None
