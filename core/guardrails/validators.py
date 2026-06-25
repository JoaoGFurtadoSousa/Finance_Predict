"""Validadores de domínio compartilhados por models e serializers."""

import re
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.core.validators import validate_email as django_validate_email

from .sanitizers import sanitize_email, sanitize_text


NAME_RE = re.compile(r"^[A-Za-zÀ-ÿ\s]{3,150}$")
INVALID_REPEATED_CPFS = {str(digit) * 11 for digit in range(10)}
INVALID_CPFS = INVALID_REPEATED_CPFS | {"12345678900"}


def validate_name(value):
    value = sanitize_text(value)
    if not value:
        raise ValidationError("Nome é obrigatório.", code="required")
    if not NAME_RE.fullmatch(value):
        raise ValidationError(
            "Nome deve ter entre 3 e 150 caracteres e conter apenas letras e espaços.",
            code="invalid_name",
        )
    return value


def normalize_cpf(value):
    return re.sub(r"[.\-\s]", "", str(value or ""))


def validate_cpf(value):
    cpf = normalize_cpf(value)
    if len(cpf) != 11 or not cpf.isdigit() or cpf in INVALID_CPFS:
        raise ValidationError("CPF inválido.", code="invalid_cpf")

    for digit_index in (9, 10):
        factor = digit_index + 1
        total = sum(int(cpf[index]) * (factor - index) for index in range(digit_index))
        check_digit = (total * 10 % 11) % 10
        if check_digit != int(cpf[digit_index]):
            raise ValidationError("CPF inválido.", code="invalid_cpf")
    return cpf


def validate_email(value):
    value = sanitize_email(value)
    django_validate_email(value)
    return value


def validate_decimal_range(
    value,
    *,
    field_label,
    minimum=None,
    maximum=None,
    minimum_inclusive=True,
):
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValidationError(
            f"{field_label} deve ser um número válido.", code="invalid_number"
        ) from exc

    if not number.is_finite():
        raise ValidationError(
            f"{field_label} deve ser um número finito.", code="numeric_overflow"
        )
    if minimum is not None:
        invalid = number < minimum if minimum_inclusive else number <= minimum
        if invalid:
            operator = "maior ou igual a" if minimum_inclusive else "maior que"
            raise ValidationError(
                f"{field_label} deve ser {operator} {minimum}.",
                code="min_value",
            )
    if maximum is not None and number > maximum:
        raise ValidationError(
            f"{field_label} deve ser menor ou igual a {maximum}.",
            code="max_value",
        )
    return number
