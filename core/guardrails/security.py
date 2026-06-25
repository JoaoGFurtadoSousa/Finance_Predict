"""Detecção de entradas hostis em campos textuais expostos pela API."""

import logging
import re
import unicodedata

from .exceptions import SecurityViolation
from .patterns import (
    PROMPT_INJECTION_PATTERNS,
    SQL_INJECTION_PATTERNS,
    XSS_PATTERNS,
)


logger = logging.getLogger("security_guardrails")


def _searchable_text(value):
    value = unicodedata.normalize("NFKD", str(value))
    return "".join(
        character for character in value if not unicodedata.combining(character)
    ).lower()


def _matches_any(value, patterns):
    return any(re.search(pattern, value, re.IGNORECASE) for pattern in patterns)


def validate_safe_text(value, field=None):
    if value in (None, ""):
        return value

    searchable = _searchable_text(value)
    threats = (
        ("sql_injection", SQL_INJECTION_PATTERNS),
        ("xss", XSS_PATTERNS),
        ("prompt_injection", PROMPT_INJECTION_PATTERNS),
    )
    for threat, patterns in threats:
        if _matches_any(searchable, patterns):
            logger.warning(
                "security_violation",
                extra={
                    "event": "blocked_payload",
                    "threat": threat,
                    "field": field,
                },
            )
            raise SecurityViolation(field=field, threat=threat)
    return value


def validate_payload_security(payload, fields=None):
    fields = set(fields or ())
    for field, value in payload.items():
        if field in fields and isinstance(value, str):
            validate_safe_text(value, field=field)
    return payload
