import re

from . import config
from .audit import log_guardrail
from .exceptions import GuardrailViolation
from .utils import iter_strings, normalize_text


# -----------------------------
# SQL INJECTION (mais realista)
# -----------------------------
SQL_PATTERNS = (
    r"\bselect\b.*\bfrom\b",
    r"\bdrop\b.*\b(table|database)\b",
    r"\bdelete\b.*\bfrom\b",
    r"\binsert\b.*\binto\b",
    r"\bupdate\b.*\bset\b",
    r"\bunion\b.*\bselect\b",
    r"or\s+1\s*=\s*1",
    r"--",
    r"#",
)


# -----------------------------
# SYSTEM ABUSE / COMMAND INJECTION
# -----------------------------
SYSTEM_COMMAND_PATTERNS = (
    r"\b(sudo|chmod|chown|rm\s+-rf)\b",
    r"\b(powershell|cmd\.exe|bash|sh)\b",
    r"(;|\|\||&&)\s*(curl|wget|sh|bash|powershell)",
)


# -----------------------------
# PROMPT INJECTION / LLM ABUSE
# -----------------------------
PROMPT_INJECTION_PATTERNS = (
    r"ignore (all|previous) instructions",
    r"you are now",
    r"act as (a|an) (system|admin|developer)",
    r"reveal (system|hidden|internal) prompt",
    r"bypass (rules|filters|guardrails)",
    r"do not follow (rules|instructions)",
)


SUSPICIOUS_SQL_KEYWORDS = {
    "select", "from", "drop", "delete", "insert", "update",
    "union", "table", "database"
}


class InputGuardrail:
    name = "INPUT"

    def validate(self, payload):
        for path, text in iter_strings(payload):

            # -----------------------------
            # LIMIT SIZE
            # -----------------------------
            if len(text) > config.MAX_INPUT_LENGTH():
                self._block(
                    "INPUT_TOO_LONG",
                    "Entrada excede tamanho permitido.",
                    path,
                    "EXCESSIVE_LENGTH",
                )

            # -----------------------------
            # NORMALIZATION
            # -----------------------------
            normalized = normalize_text(text)
            normalized = re.sub(r"[\s]+", " ", normalized.lower())

            # -----------------------------
            # CONTROL CHARS
            # -----------------------------
            if re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", text):
                self._block(
                    "CONTROL_CHARS",
                    "Entrada contém caracteres inválidos.",
                    path,
                    "SUSPICIOUS_CHARACTERS",
                )

            # -----------------------------
            # SQL INJECTION CHECK
            # -----------------------------
            if any(re.search(p, normalized) for p in SQL_PATTERNS):
                self._block(
                    "SQL_INJECTION",
                    "Padrão SQL suspeito detectado.",
                    path,
                    "SQL_INJECTION",
                )

            # fallback heurístico (pega variações tipo SELECT * FROM)
            tokens = set(normalized.split())
            if len(tokens.intersection(SUSPICIOUS_SQL_KEYWORDS)) >= 3:
                self._block(
                    "SQL_KEYWORD_CLUSTER",
                    "Cluster de palavras SQL detectado.",
                    path,
                    "SQL_INJECTION",
                )

            # -----------------------------
            # SYSTEM COMMAND INJECTION
            # -----------------------------
            if any(re.search(p, normalized) for p in SYSTEM_COMMAND_PATTERNS):
                self._block(
                    "SYSTEM_COMMAND",
                    "Comando de sistema detectado.",
                    path,
                    "SYSTEM_COMMAND",
                )

            # -----------------------------
            # PROMPT INJECTION (MUITO IMPORTANTE no seu caso)
            # -----------------------------
            if any(re.search(p, normalized) for p in PROMPT_INJECTION_PATTERNS):
                self._block(
                    "PROMPT_INJECTION",
                    "Tentativa de manipulação de instruções detectada.",
                    path,
                    "PROMPT_INJECTION",
                )

        return payload

    # -----------------------------
    # BLOCK HANDLER
    # -----------------------------
    def _block(self, reason, message, path, threat_type):
        log_guardrail(self.name, reason, threat_type)

        raise GuardrailViolation(
            self.name,
            reason,
            message,
            {"field": path} if path else None
        )