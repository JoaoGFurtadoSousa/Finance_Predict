"""Troca promessas determinísticas por linguagem financeira responsável."""

import re

from .audit import log_guardrail


REPLACEMENTS = (
    (re.compile(r"\blucro garantido\b", re.I), "possibilidade de lucro"),
    (re.compile(r"\bretorno garantido\b", re.I), "retorno potencial"),
    (re.compile(r"\bsem risco\b", re.I), "com riscos que devem ser avaliados"),
    (
        re.compile(r"\bessa a[cç][aã]o vai subir\b", re.I),
        "essa ação pode apresentar valorização",
    ),
    (re.compile(r"\bganho certo\b", re.I), "possibilidade de ganho"),
)


class ComplianceGuardrail:
    name = "COMPLIANCE"

    def sanitize(self, recommendation):
        if isinstance(recommendation, str):
            return self._sanitize_text(recommendation)
        if isinstance(recommendation, dict):
            return {
                key: self.sanitize(value) for key, value in recommendation.items()
            }
        if isinstance(recommendation, list):
            return [self.sanitize(value) for value in recommendation]
        if isinstance(recommendation, tuple):
            return tuple(self.sanitize(value) for value in recommendation)
        return recommendation

    def contains_guarantees(self, recommendation):
        text = str(recommendation)
        return any(pattern.search(text) for pattern, _ in REPLACEMENTS)

    def _sanitize_text(self, text):
        result = text
        for pattern, replacement in REPLACEMENTS:
            if pattern.search(result):
                log_guardrail(self.name, "PROHIBITED_CLAIM_REWRITTEN", "COMPLIANCE")
                result = pattern.sub(replacement, result)
        return result
