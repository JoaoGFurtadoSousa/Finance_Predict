from decimal import Decimal

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
            objetivo_de_vida="Preservacao",
            tempo_estimado_retorno=3,
            valor_desejado_acumulado=Decimal("30000.00"),
            preocupacao_atual="Quero preservar capital no curto prazo.",
            tipo_de_investidor="Conservador",
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
Resumo da estratÃ©gia

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

    @staticmethod
    def _valid_text():
        return """
Resumo da estratÃ©gia

Carteira recomendada:

Nome do investimento: Tesouro Selic
Valor recomendado para investir: R$ 500,00
Motivo da escolha: Reserva com liquidez.

Nome do investimento: CDB Liquidez
Valor recomendado para investir: R$ 500,00
Motivo da escolha: Complementa a renda fixa.

Total investido: R$ 1000,00
""".strip()
