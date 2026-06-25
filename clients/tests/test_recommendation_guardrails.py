from django.test import SimpleTestCase, override_settings

from clients.guardrails import GuardrailViolation
from clients.guardrails.profile_matching import ProfileMatchingGuardrail
from clients.guardrails.recommendation import RecommendationGuardrail


class ProfileMatchingGuardrailTests(SimpleTestCase):
    def test_blocks_speculative_asset_for_conservative_profile(self):
        with self.assertRaises(GuardrailViolation) as raised:
            ProfileMatchingGuardrail().validate(
                {"asset": "Bitcoin", "justification": "Diversificação"},
                "Conservador",
            )
        self.assertEqual(raised.exception.reason, "PROFILE_MISMATCH")

    def test_allows_fixed_income_for_conservative_profile(self):
        recommendation = {"asset": "Tesouro Selic"}
        self.assertIs(
            ProfileMatchingGuardrail().validate(recommendation, "Conservador"),
            recommendation,
        )


class RecommendationGuardrailTests(SimpleTestCase):
    def test_blocks_dangerous_instruction(self):
        with self.assertRaises(GuardrailViolation):
            RecommendationGuardrail().validate("Invista tudo em um único ativo")

    @override_settings(MAX_SINGLE_ASSET_PERCENT=30)
    def test_blocks_excessive_single_asset_allocation(self):
        data = {"asset": "CDB", "percentage": 50}
        with self.assertRaises(GuardrailViolation) as raised:
            RecommendationGuardrail().validate(data)
        self.assertEqual(
            raised.exception.reason, "EXCESSIVE_SINGLE_ASSET_CONCENTRATION"
        )

    @override_settings(MAX_CRYPTO_PERCENT=10)
    def test_blocks_excessive_crypto_allocation(self):
        data = {"asset": "Bitcoin", "percentage": 20}
        with self.assertRaises(GuardrailViolation) as raised:
            RecommendationGuardrail().validate(data)
        self.assertEqual(raised.exception.reason, "EXCESSIVE_CRYPTO_CONCENTRATION")

    @override_settings(MAX_LEVERAGE=1)
    def test_blocks_excessive_leverage(self):
        with self.assertRaises(GuardrailViolation) as raised:
            RecommendationGuardrail().validate({"leverage": 2})
        self.assertEqual(raised.exception.reason, "EXCESSIVE_LEVERAGE")
