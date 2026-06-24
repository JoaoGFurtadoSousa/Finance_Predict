"""Remove PII de texto livre antes que ele alcance agentes ou logs."""

import re


PII_PATTERNS = (
    ("CPF_REMOVIDO", re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")),
    (
        "CREDIT_CARD_REMOVIDO",
        re.compile(r"\b(?:\d[ -]*?){13,19}\b"),
    ),
    (
        "RG_REMOVIDO",
        re.compile(r"\b(?:rg\s*[:.-]?\s*)\d{1,2}\.?\d{3}\.?\d{3}-?[\dXx]\b", re.I),
    ),
    (
        "PIX_REMOVIDO",
        re.compile(
            r"\b(?:pix|chave pix)\s*[:=-]\s*(?:[\w.+-]+@[\w.-]+|\+?\d[\d\s().-]{7,}|[0-9a-f-]{32,36})",
            re.I,
        ),
    ),
    (
        "BANK_ACCOUNT_REMOVIDO",
        re.compile(
            r"\b(?:conta|ag[eê]ncia|banco)\s*[:=-]\s*[\d.-]{3,}\b", re.I
        ),
    ),
    ("CEP_REMOVIDO", re.compile(r"\b\d{5}-?\d{3}\b")),
)


class PIIGuardrail:
    name = "PII"

    def sanitize_text(self, text):
        sanitized = text
        for token, pattern in PII_PATTERNS:
            sanitized = pattern.sub(f"[{token}]", sanitized)
        return sanitized

    def sanitize(self, payload, excluded_fields=None):
        excluded_fields = set(excluded_fields or ())
        if isinstance(payload, dict):
            return {
                key: (
                    value
                    if key in excluded_fields
                    else self.sanitize(value, excluded_fields)
                )
                for key, value in payload.items()
            }
        if isinstance(payload, list):
            return [self.sanitize(item, excluded_fields) for item in payload]
        if isinstance(payload, tuple):
            return tuple(self.sanitize(item, excluded_fields) for item in payload)
        if isinstance(payload, str):
            return self.sanitize_text(payload)
        return payload
