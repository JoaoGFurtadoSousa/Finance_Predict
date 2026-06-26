"""Camada independente de proteção para entradas e recomendações financeiras."""

from .exceptions import GuardrailViolation
from .pipeline import InvestmentGuardrails

__all__ = ["GuardrailViolation", "InvestmentGuardrails"]
