"""Normalização conservadora de texto antes da validação e persistência."""

import re
import unicodedata


_WHITESPACE_RE = re.compile(r"\s+")


def _is_disallowed_character(character):
    category = unicodedata.category(character)
    return category in {"Cf", "Cs", "Co", "Cn"} or (
        category.startswith("C") and character not in "\t\n\r"
    )


def sanitize_text(value):
    if not isinstance(value, str):
        return value

    value = unicodedata.normalize("NFC", value.strip())
    value = "".join(
        character
        for character in value
        if not _is_disallowed_character(character)
    )
    return _WHITESPACE_RE.sub(" ", value).strip()


def sanitize_email(value):
    value = sanitize_text(value)
    return value.lower() if isinstance(value, str) else value


def sanitize_payload(payload):
    """Sanitiza recursivamente strings sem modificar o objeto recebido."""
    if isinstance(payload, dict):
        return {
            key: (
                sanitize_email(item)
                if str(key).lower() == "email"
                else sanitize_payload(item)
            )
            for key, item in payload.items()
        }
    if isinstance(payload, list):
        return [sanitize_payload(item) for item in payload]
    if isinstance(payload, tuple):
        return tuple(sanitize_payload(item) for item in payload)
    return sanitize_text(payload)
