"""Orquestra os guardrails sem acoplar a camada a views, ML ou agentes."""

from .compliance import ComplianceGuardrail
from .hallucination import HallucinationGuardrail
from .input_guardrail import InputGuardrail
from .output import OutputGuardrail
from .pii import PIIGuardrail
from .profile_matching import ProfileMatchingGuardrail
from .prompt_injection import PromptInjectionGuardrail
from .recommendation import RecommendationGuardrail
from .sources import SourceValidationGuardrail
from .suitability import SuitabilityGuardrail


class InvestmentGuardrails:
    def __init__(self):
        self.input = InputGuardrail()
        self.pii = PIIGuardrail()
        self.prompt_injection = PromptInjectionGuardrail()
        self.suitability = SuitabilityGuardrail()
        self.profile_matching = ProfileMatchingGuardrail()
        self.recommendation = RecommendationGuardrail()
        self.compliance = ComplianceGuardrail()
        self.hallucination = HallucinationGuardrail()
        self.sources = SourceValidationGuardrail()
        self.output = OutputGuardrail()

    def process_input(self, payload, pii_excluded_fields=None):
        self.input.validate(payload)
        self.prompt_injection.validate(payload)
        return self.pii.sanitize(payload, excluded_fields=pii_excluded_fields)

    def validate_suitability(self, context):
        return self.suitability.validate(context)

    def process_output(self, recommendation, profile):
        checklist = {
            "profile_match": False,
            "compliance_ok": False,
            "has_sources": False,
            "no_guarantees": False,
            "no_excessive_concentration": False,
            "no_hallucination": False,
        }

        self.profile_matching.validate(recommendation, profile)
        checklist["profile_match"] = True
        self.recommendation.validate(recommendation)
        checklist["no_excessive_concentration"] = True
        result = self.compliance.sanitize(recommendation)
        checklist["compliance_ok"] = True
        checklist["no_guarantees"] = not self.compliance.contains_guarantees(result)
        self.sources.validate(result)
        checklist["has_sources"] = True
        self.hallucination.validate(result)
        checklist["no_hallucination"] = True
        return self.output.validate(result, checklist)
