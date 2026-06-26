import re
import unicodedata


def normalize_text(value):
    text = unicodedata.normalize("NFKD", str(value))
    return "".join(char for char in text if not unicodedata.combining(char)).lower()


def iter_strings(value, path=""):
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for key, item in value.items():
            child_path = f"{path}.{key}" if path else str(key)
            yield from iter_strings(item, child_path)
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            yield from iter_strings(item, f"{path}[{index}]")


def find_percentage(text, labels):
    normalized = normalize_text(text)
    label_pattern = "|".join(re.escape(normalize_text(label)) for label in labels)
    patterns = (
        rf"(\d+(?:[.,]\d+)?)\s*%\s*(?:em|de)?\s*(?:{label_pattern})",
        rf"(?:{label_pattern})[^0-9%]{{0,30}}(\d+(?:[.,]\d+)?)\s*%",
    )
    for pattern in patterns:
        match = re.search(pattern, normalized, re.IGNORECASE)
        if match:
            return float(match.group(1).replace(",", "."))
    return None
