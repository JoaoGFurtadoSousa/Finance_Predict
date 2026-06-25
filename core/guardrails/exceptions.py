"""Exceções e tradução consistente de erros para a API REST."""

import logging

from django.core.exceptions import ValidationError as DjangoValidationError
from django_ratelimit.exceptions import Ratelimited
from rest_framework import status
from rest_framework.exceptions import (
    Throttled,
    ValidationError as DRFValidationError,
)
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


logger = logging.getLogger("validation_guardrails")


class SecurityViolation(DjangoValidationError):
    def __init__(self, field=None, threat=None):
        self.field = field
        self.threat = threat
        super().__init__(
            "Payload bloqueado por política de segurança.",
            code="blocked_payload",
        )


def security_error_detail(exc):
    return {
        "success": False,
        "message": "Payload bloqueado por política de segurança.",
        "code": "blocked_payload",
        **({"field": exc.field} if exc.field else {}),
    }


def _first_error(detail):
    if isinstance(detail, dict):
        field, value = next(iter(detail.items()))
        nested_field, message = _first_error(value)
        return (field if field not in {"non_field_errors", "detail"} else nested_field), message
    if isinstance(detail, (list, tuple)) and detail:
        return _first_error(detail[0])
    return None, str(detail)


def api_exception_handler(exc, context):
    if isinstance(exc, (Ratelimited, Throttled)):
        logger.warning("blocked_payload", extra={"event": "rate_limit", "threat": "rate_limit"})
        return Response(
            {
                "success": False,
                "message": "Limite de requisições excedido. Tente novamente em breve.",
            },
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )

    response = drf_exception_handler(exc, context)
    if response is None:
        return None

    if isinstance(exc, DRFValidationError):
        field, message = _first_error(response.data)
        logger.info(
            "validation_error",
            extra={"event": "validation_error", "field": field},
        )
        if "Payload bloqueado por política de segurança." in message:
            response.data = {
                "success": False,
                "message": "Payload bloqueado por política de segurança.",
                **({"field": field} if field else {}),
            }
        else:
            response.data = {
                "success": False,
                **({"field": field} if field else {}),
                "message": message,
            }
    return response
