from django.test import SimpleTestCase

from clients.guardrails import GuardrailViolation, InvestmentGuardrails
from clients.guardrails.compliance import ComplianceGuardrail
from clients.guardrails.hallucination import HallucinationGuardrail
from clients.guardrails.output import OutputGuardrail
from clients.guardrails.sources import SourceValidationGuardrail


def valid_recommendation():
    return {
        "recommendations": [
            {
                "asset": "CDB",
                "percentage": 30,
                "justification": "Liquidez e risco compatíveis com o perfil.",
                "sources": ["https://www.b3.com.br/"],
            }
        ]
    }


class ComplianceGuardrailTests(SimpleTestCase):
    def test_rewrites_prohibited_claims(self):
        guardrail = ComplianceGuardrail()
        result = guardrail.sanitize("Este produto oferece retorno garantido e sem risco.")
        self.assertNotIn("retorno garantido", result.lower())
        self.assertNotIn("sem risco", result.lower())
        self.assertFalse(guardrail.contains_guarantees(result))


class EvidenceAndSourceGuardrailTests(SimpleTestCase):
    def test_blocks_missing_source(self):
        data = {"asset": "CDB", "justification": "Baixa volatilidade", "sources": []}
        with self.assertRaises(GuardrailViolation):
            SourceValidationGuardrail().validate(data)

    def test_blocks_invalid_source(self):
        data = {
            "asset": "CDB",
            "justification": "Baixa volatilidade",
            "sources": ["fonte desconhecida"],
        }
        with self.assertRaises(GuardrailViolation):
            SourceValidationGuardrail().validate(data)

    def test_blocks_missing_evidence(self):
        data = {"asset": "CDB", "sources": ["https://www.b3.com.br/"]}
        with self.assertRaises(GuardrailViolation):
            HallucinationGuardrail().validate(data)


class OutputGuardrailTests(SimpleTestCase):
    def test_fails_closed_when_check_is_false(self):
        checklist = {
            "profile_match": True,
            "compliance_ok": True,
            "has_sources": True,
            "no_guarantees": False,
            "no_excessive_concentration": True,
            "no_hallucination": True,
        }
        with self.assertRaises(GuardrailViolation) as raised:
            OutputGuardrail().validate({}, checklist)
        self.assertIn("no_guarantees", raised.exception.details["failed_checks"])

    def test_complete_pipeline_accepts_safe_recommendation(self):
        result = InvestmentGuardrails().process_output(
            valid_recommendation(), "Conservador"
        )
        self.assertEqual(result["recommendations"][0]["asset"], "CDB")

    def test_complete_pipeline_rewrites_compliance_language(self):
        data = valid_recommendation()
        data["recommendations"][0]["justification"] = (
            "Há retorno garantido segundo dados históricos."
        )
        result = InvestmentGuardrails().process_output(data, "Conservador")
        self.assertNotIn(
            "retorno garantido",
            result["recommendations"][0]["justification"].lower(),
        )
