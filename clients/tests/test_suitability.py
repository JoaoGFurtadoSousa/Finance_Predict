from django.test import SimpleTestCase

from clients.guardrails import GuardrailViolation
from clients.guardrails.suitability import SuitabilityGuardrail


class SuitabilityGuardrailTests(SimpleTestCase):
    def test_requests_missing_data(self):
        with self.assertRaises(GuardrailViolation) as raised:
            SuitabilityGuardrail().validate({"profile": "Moderado"})
        self.assertIn(
            "objetivo financeiro", raised.exception.details["missing_fields"]
        )

    def test_accepts_current_client_field_names(self):
        context = {
            "tipo_de_investidor": "Moderado",
            "objetivo_de_vida": "Aposentadoria",
            "tempo_estimado_retorno": 10,
            "aporte_mensal": 1000,
        }
        self.assertIs(SuitabilityGuardrail().validate(context), context)
