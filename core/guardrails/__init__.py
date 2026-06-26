"""Guardrails reutilizáveis para entradas recebidas pela API."""

from .exceptions import SecurityViolation
from .sanitizers import sanitize_email, sanitize_text
from .security import validate_safe_text

__all__ = [
    "SecurityViolation",
    "sanitize_email",
    "sanitize_text",
    "validate_safe_text",
]
