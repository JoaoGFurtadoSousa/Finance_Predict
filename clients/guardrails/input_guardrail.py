"""Validação genérica contra payloads hostis ou excessivos."""

import re

from . import config
from .audit import log_guardrail
from .exceptions import GuardrailViolation
from .utils import iter_strings, normalize_text


SQL_PATTERNS = (
    r"\bunion\s+(?:all\s+)?select\b",
    r"\bdrop\s+(?:table|database)\b",
    r"\bdelete\s+from\b",
    r"\binsert\s+into\b",
    r"\bupdate\s+\w+\s+set\b",
    r"(?:'|\")\s*or\s+(?:'?\w+'?\s*=\s*'?\w+|1\s*=\s*1)",
    r"--\s*$",
)
SYSTEM_COMMAND_PATTERNS = (
    r"(?:^|\s)(?:sudo|chmod|chown|rm\s+-rf|powershell|cmd\.exe)\b",
    r"(?:^|\s)(?:curl|wget)\s+https?://",
    r"(?:;|&&|\|\|)\s*(?:sh|bash|cmd|powershell)\b",
)


class InputGuardrail:
    name = "INPUT"

    def validate(self, payload):
        for path, text in iter_strings(payload):
            if len(text) > config.MAX_INPUT_LENGTH():
                self._block(
                    "INPUT_TOO_LONG",
                    "A entrada excede o tamanho máximo permitido.",
                    path,
                    "EXCESSIVE_LENGTH",
                )

            normalized = normalize_text(text)
            if re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", text):
                self._block(
                    "SUSPICIOUS_CHARACTERS",
                    "A entrada contém caracteres de controle não permitidos.",
                    path,
                    "SUSPICIOUS_CHARACTERS",
                )
            if any(re.search(pattern, normalized) for pattern in SQL_PATTERNS):
                self._block(
                    "SQL_INJECTION",
                    "A entrada contém uma sequência não permitida.",
                    path,
                    "SQL_INJECTION",
                )
            if any(
                re.search(pattern, normalized) for pattern in SYSTEM_COMMAND_PATTERNS
            ):
                self._block(
                    "SYSTEM_COMMAND",
                    "Comandos de sistema não são permitidos.",
                    path,
                    "SYSTEM_COMMAND",
                )
        return payload

    def _block(self, reason, message, path, threat_type):
        log_guardrail(self.name, reason, threat_type)
        raise GuardrailViolation(
            self.name, reason, message, {"field": path} if path else None
        )
