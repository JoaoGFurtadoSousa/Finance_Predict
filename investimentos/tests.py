from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase

from clients.models import Client
from investimentos.models import ClasseAtivo, Investimento, PerfilInvestidor
from investimentos.services.recommendation_audit_skill import (
    audit_recommendation,
    audited_recommendation_text,
    parse_recommendation_text,
)


class RecommendationAuditSkillTests(TestCase):
    def setUp(self):
        self.profile = PerfilInvestidor.objects.create(nome="Conservador")
        self.asset_class = ClasseAtivo.objects.create(
            nome="Renda Fixa",
            perfil=self.profile,
            risco=1,
        )
        Investimento.objects.create(
            nome="Tesouro Selic",
            ticker="SELIC11",
            tipo_investimento=self.asset_class,
            rentabilidade_anual=Decimal("10.00"),
            volatilidade=Decimal("1.00"),
            liquidez_dias=1,
            risco=1,
        )
        Investimento.objects.create(
            nome="CDB Liquidez",
            ticker="CDBL11",
            tipo_investimento=self.asset_class,
            rentabilidade_anual=Decimal("11.00"),
            volatilidade=Decimal("1.50"),
            liquidez_dias=30,
            risco=2,
        )
        self.client = Client.objects.create(
            nome="Maria Silva",
            cpf="52998224725",
            email="maria.audit@example.com",
            idade=30,
            renda_atual=Decimal("5000.00"),
            aporte_mensal=Decimal("1000.00"),
            reserva_de_emergencia=True,
            valor_armazenado_reserva_emergencia=Decimal("10000.00"),
            possui_dividas=False,
            tolerancia_volatilidade=3,
            experiencia_em_investimentos="Iniciante",
            aceitacao_perda_percentual=5,
            liquidez_necessaria="Imediata",
            objetivo_de_vida="Aposentadoria",
            tempo_estimado_retorno=3,
            valor_desejado_acumulado=Decimal("30000.00"),
            preocupacao_atual="Quero preservar capital no curto prazo.",
            tipo_de_investidor="Conservador",
        )
        self.aggressive_profile = PerfilInvestidor.objects.create(nome="Agressivo")
        self.aggressive_class = ClasseAtivo.objects.create(
            nome="Internacional",
            perfil=self.profile,
            risco=5,
        )
        Investimento.objects.create(
            nome="Hashdex Crypto",
            ticker="HASH11",
            tipo_investimento=self.aggressive_class,
            rentabilidade_anual=Decimal("18.00"),
            volatilidade=Decimal("9.00"),
            liquidez_dias=3,
            risco=5,
        )
        self.aggressive_client = Client.objects.create(
            nome="Joao Silva",
            cpf="12345678909",
            email="joao.audit@example.com",
            idade=32,
            renda_atual=Decimal("9000.00"),
            aporte_mensal=Decimal("2000.00"),
            reserva_de_emergencia=True,
            valor_armazenado_reserva_emergencia=Decimal("15000.00"),
            possui_dividas=False,
            tolerancia_volatilidade=8,
            experiencia_em_investimentos="Intermediario",
            aceitacao_perda_percentual=25,
            liquidez_necessaria="Longo_prazo",
            objetivo_de_vida="Aposentadoria",
            tempo_estimado_retorno=10,
            valor_desejado_acumulado=Decimal("200000.00"),
            preocupacao_atual="Quero crescer patrimonio no longo prazo.",
            tipo_de_investidor="Agressivo",
        )

    def test_parser_extracts_investments_from_agent_text(self):
        parsed = parse_recommendation_text(self._valid_text())
        self.assertEqual(parsed["investimentos"][0]["nome"], "Tesouro Selic")
        self.assertEqual(parsed["investimentos"][1]["valor"], "R$ 500,00")

    def test_audit_approves_valid_recommendation(self):
        result = audit_recommendation(self.client, self._valid_text())
        self.assertEqual(result["status"], "approved")
        self.assertEqual(result["inconsistencies"], [])

    def test_audit_rejects_unknown_investment(self):
        text = self._valid_text().replace("CDB Liquidez", "Bitcoin XYZ")
        result = audit_recommendation(self.client, text)
        self.assertEqual(result["status"], "rejected")
        self.assertIn("nao existe no banco de dados", result["message"])

    def test_audit_rejects_total_mismatch(self):
        text = self._valid_text().replace("R$ 500,00", "R$ 250,00", 1)
        result = audit_recommendation(self.client, text)
        self.assertEqual(result["status"], "rejected")
        self.assertIn("Total recomendado: R$ 750,00", result["message"])
        self.assertIn("Total esperado: R$ 1.000,00", result["message"])

    def test_parser_accepts_blank_lines_and_missing_section_headers(self):
        parsed = parse_recommendation_text(
            """
Nome do investimento: Tesouro Selic

Valor recomendado para investir: R$ 500,00

Motivo da escolha: Reserva com liquidez.

Nome do investimento: CDB Liquidez

Valor recomendado para investir: R$ 500,00
""".strip()
        )
        self.assertEqual(len(parsed["investimentos"]), 2)
        self.assertEqual(parsed["investimentos"][0]["nome"], "Tesouro Selic")
        self.assertEqual(parsed["investimentos"][1]["valor"], "R$ 500,00")

    def test_audit_accepts_money_formats_with_and_without_currency_symbol(self):
        text = """
Resumo da estrategia

Carteira recomendada:

Nome do investimento: Tesouro Selic
Valor recomendado para investir: R$500,00

Nome do investimento: CDB Liquidez
Valor recomendado para investir: 500
""".strip()
        result = audit_recommendation(self.client, text)
        self.assertEqual(result["status"], "approved")
        self.assertEqual(result["inconsistencies"], [])

    def test_audited_recommendation_appends_error_without_changing_portfolio(self):
        text = self._valid_text().replace("R$ 500,00", "R$ 800,00", 1)
        audited = audited_recommendation_text(self.client, text)
        self.assertIn("Tesouro Selic", audited)
        self.assertIn("ERRO DE AUDITORIA", audited)
        self.assertIn("representa 80%", audited)

    def test_audit_does_not_flag_aggressive_asset_when_risk_is_allowed(self):
        text = """
Carteira recomendada:

Nome do investimento: Hashdex Crypto
Valor recomendado para investir: R$ 1000,00
Motivo da escolha: Exposicao a crescimento.

Nome do investimento: Hashdex Crypto
Valor recomendado para investir: R$ 1000,00
Motivo da escolha: Complementa a estrategia.
""".strip()
        result = audit_recommendation(self.aggressive_client, text)
        self.assertEqual(result["status"], "approved")
        self.assertEqual(result["inconsistencies"], [])

    def test_audit_matches_investment_names_after_normalization(self):
        text = """
Carteira recomendada:

Nome do investimento:   hashdex   crypto
Valor recomendado para investir: R$ 1000,00
Motivo da escolha: Exposicao a crescimento.

Nome do investimento: Hashdex Crypto
Valor recomendado para investir: R$ 1000,00
Motivo da escolha: Complementa a estrategia.
""".strip()
        result = audit_recommendation(self.aggressive_client, text)
        self.assertEqual(result["status"], "approved")
        self.assertEqual(result["inconsistencies"], [])

    @patch("investimentos.agents.agente_conservador.safe_send_portfolio_email")
    @patch("investimentos.agents.agente_conservador.initialize_agent")
    def test_agent_sends_email_after_approved_audit(
        self, mock_initialize_agent, mock_send_email
    ):
        mock_initialize_agent.return_value.invoke.return_value = {
            "output": self._valid_text()
        }

        from investimentos.agents.agente_conservador import agente_conservador

        result = agente_conservador(self.client)

        self.assertIn("Tesouro Selic", result)
        mock_send_email.assert_called_once_with(self.client, self._valid_text())

    @patch("investimentos.agents.agente_conservador.safe_send_portfolio_email")
    @patch("investimentos.agents.agente_conservador.initialize_agent")
    def test_agent_does_not_send_email_when_audit_fails(
        self, mock_initialize_agent, mock_send_email
    ):
        invalid_text = self._valid_text().replace("R$ 500,00", "R$ 800,00", 1)
        mock_initialize_agent.return_value.invoke.return_value = {
            "output": invalid_text
        }

        from investimentos.agents.agente_conservador import agente_conservador

        result = agente_conservador(self.client)

        self.assertIn("ERRO DE AUDITORIA", result)
        mock_send_email.assert_not_called()

    @patch("clients.services.email_service.logger")
    @patch("clients.services.email_service.send_portfolio_email")
    def test_safe_email_delivery_failure_does_not_raise(
        self, mock_send_portfolio_email, mock_logger
    ):
        from clients.services.email_service import safe_send_portfolio_email

        mock_send_portfolio_email.side_effect = RuntimeError("smtp unavailable")

        safe_send_portfolio_email(self.client, self._valid_text())

        mock_send_portfolio_email.assert_called_once_with(self.client, self._valid_text())
        mock_logger.exception.assert_called_once()

    @staticmethod
    def _valid_text():
        return """
Resumo da estrategia

Carteira recomendada:

Nome do investimento: Tesouro Selic
Valor recomendado para investir: R$ 500,00
Motivo da escolha: Reserva com liquidez.

Nome do investimento: CDB Liquidez
Valor recomendado para investir: R$ 500,00
Motivo da escolha: Complementa a renda fixa.

Total investido: R$ 1000,00
""".strip()
