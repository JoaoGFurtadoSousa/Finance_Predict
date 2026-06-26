"""Bloqueia tentativas de alterar instruções ou assumir privilégios."""

import re

from .audit import log_guardrail
from .exceptions import GuardrailViolation
from .utils import iter_strings, normalize_text


PROMPT_INJECTION_PATTERNS = (
    r"\bignore (?:all |the )?(?:previous|prior) instructions?\b",
    r"\bignore (?:suas|as) instrucoes\b",
    r"\bforget (?:all |the )?(?:previous|prior) instructions?\b",
    r"\byou are now\b",
    r"\b(?:system override|developer mode|sudo mode)\b",
    r"\bact as\b",
    r"\breveal (?:the )?(?:system|developer) prompt\b",
    r"\bmostre (?:o )?prompt (?:do )?sistema\b",
    r"\bjailbreak\b",
)


class PromptInjectionGuardrail:
    name = "PROMPT_INJECTION"

    def validate(self, payload):
        for path, text in iter_strings(payload):
            normalized = normalize_text(text)
            if any(
                re.search(pattern, normalized)
                for pattern in PROMPT_INJECTION_PATTERNS
            ):
                reason = "INSTRUCTION_OVERRIDE_ATTEMPT"
                log_guardrail(self.name, reason, "PROMPT_INJECTION")
                raise GuardrailViolation(
                    self.name,
                    reason,
                    "A entrada contém uma tentativa de manipular as instruções.",
                    {"field": path} if path else None,
                )
        return payload
