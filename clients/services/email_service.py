import html
import logging
from datetime import datetime

from django.conf import settings
from django.core.mail import EmailMultiAlternatives


logger = logging.getLogger("validation_guardrails")


def send_portfolio_email(client, portfolio_text):
    subject = "Sua carteira personalizada de investimentos esta pronta"
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@financepredict.local")
    recipient_list = [client.email]
    text_content = _build_text_content(client, portfolio_text)
    html_content = _build_html_content(client, portfolio_text)

    message = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=from_email,
        to=recipient_list,
    )
    message.attach_alternative(html_content, "text/html")
    message.send(fail_silently=False)


def safe_send_portfolio_email(client, portfolio_text):
    try:
        send_portfolio_email(client, portfolio_text)
    except Exception:
        logger.exception(
            "portfolio_email_failed",
            extra={"client_email": client.email, "event": "portfolio_email_failed"},
        )


def _build_text_content(client, portfolio_text):
    return (
        f"Olá, {client.nome}!\n\n"
        "Sua carteira personalizada foi gerada com sucesso.\n\n"
        "Nossa Inteligencia Artificial analisou o seu perfil de investidor e elaborou "
        "uma estrategia de investimentos compativel com seus objetivos financeiros.\n\n"
        "Resumo do seu perfil:\n"
        f"- Perfil do investidor: {client.tipo_de_investidor}\n"
        f"- Aporte mensal: {_format_money(client.aporte_mensal)}\n"
        f"- Prazo de investimento: {client.tempo_estimado_retorno} anos\n"
        f"- Objetivo de vida: {client.objetivo_de_vida}\n\n"
        "Carteira recomendada:\n"
        f"{portfolio_text}\n\n"
        "Carteira Validada\n"
        "Esta recomendacao passou pela Skill de Auditoria do Finance Predict.\n"
        "Foram verificadas automaticamente:\n"
        "- compatibilidade entre perfil e risco dos ativos;\n"
        "- existencia dos investimentos na base de dados;\n"
        "- distribuicao integral do aporte mensal;\n"
        "- concentracao excessiva da carteira;\n"
        "- consistencia das recomendacoes geradas pela IA.\n\n"
        "Importante\n"
        "Esta carteira possui finalidade educacional e nao constitui recomendacao oficial de investimento.\n"
        "Sempre considere sua situacao financeira antes de investir.\n\n"
        f"Finance Predict\nSistema Inteligente de Recomendacao de Investimentos\nTrabalho de Conclusao de Curso\n{datetime.now().year}\n"
    )


def _build_html_content(client, portfolio_text):
    escaped_portfolio = html.escape(str(portfolio_text or "")).replace("\n", "<br>")
    current_year = datetime.now().year

    return f"""
<!DOCTYPE html>
<html lang="pt-BR">
  <body style="margin:0;padding:0;background-color:#f1f5f9;font-family:Arial,sans-serif;color:#0f172a;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color:#f1f5f9;padding:24px 12px;">
      <tr>
        <td align="center">
          <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:680px;background-color:#ffffff;border-radius:24px;overflow:hidden;">
            <tr>
              <td style="background-color:#0f172a;padding:28px 24px;text-align:center;">
                <div style="color:#93c5fd;font-size:13px;font-weight:bold;letter-spacing:1px;text-transform:uppercase;">Finance Predict</div>
                <h1 style="margin:10px 0 0;font-size:28px;line-height:36px;color:#ffffff;">Sua carteira personalizada esta pronta</h1>
              </td>
            </tr>
            <tr>
              <td style="padding:32px 24px 16px;">
                <p style="margin:0 0 12px;font-size:16px;line-height:24px;">Ola, {html.escape(client.nome)}!</p>
                <p style="margin:0;font-size:15px;line-height:24px;color:#334155;">
                  Sua carteira personalizada foi gerada com sucesso. Nossa Inteligencia Artificial analisou o seu perfil de investidor e elaborou uma estrategia de investimentos compativel com seus objetivos financeiros.
                </p>
              </td>
            </tr>
            <tr>
              <td style="padding:8px 24px 16px;">
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color:#eff6ff;border:1px solid #bfdbfe;border-radius:18px;">
                  <tr>
                    <td style="padding:20px;">
                      <h2 style="margin:0 0 16px;font-size:18px;line-height:24px;color:#0f172a;">Resumo do seu perfil</h2>
                      <p style="margin:0 0 8px;font-size:14px;line-height:22px;"><strong>Perfil do investidor:</strong> {html.escape(str(client.tipo_de_investidor or "-"))}</p>
                      <p style="margin:0 0 8px;font-size:14px;line-height:22px;"><strong>Aporte mensal:</strong> {_format_money(client.aporte_mensal)}</p>
                      <p style="margin:0 0 8px;font-size:14px;line-height:22px;"><strong>Prazo de investimento:</strong> {client.tempo_estimado_retorno} anos</p>
                      <p style="margin:0;font-size:14px;line-height:22px;"><strong>Objetivo de vida:</strong> {html.escape(str(client.objetivo_de_vida))}</p>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
            <tr>
              <td style="padding:8px 24px 16px;">
                <h2 style="margin:0 0 12px;font-size:18px;line-height:24px;color:#0f172a;">Carteira recomendada</h2>
                <div style="background-color:#f8fafc;border:1px solid #e2e8f0;border-radius:18px;padding:20px;box-shadow:0 10px 25px rgba(15,23,42,0.06);font-size:14px;line-height:24px;color:#334155;">
                  {escaped_portfolio}
                </div>
              </td>
            </tr>
            <tr>
              <td style="padding:8px 24px 16px;">
                <div style="background-color:#ecfdf5;border:1px solid #86efac;border-radius:18px;padding:20px;">
                  <h2 style="margin:0 0 12px;font-size:18px;line-height:24px;color:#166534;">Carteira Validada</h2>
                  <p style="margin:0 0 12px;font-size:14px;line-height:22px;color:#166534;">Esta recomendacao passou pela Skill de Auditoria do Finance Predict.</p>
                  <p style="margin:0;font-size:14px;line-height:24px;color:#166534;">
                    • compatibilidade entre perfil e risco dos ativos;<br>
                    • existencia dos investimentos na base de dados;<br>
                    • distribuicao integral do aporte mensal;<br>
                    • concentracao excessiva da carteira;<br>
                    • consistencia das recomendacoes geradas pela IA.
                  </p>
                </div>
              </td>
            </tr>
            <tr>
              <td style="padding:8px 24px 32px;">
                <div style="background-color:#fff7ed;border:1px solid #fdba74;border-radius:18px;padding:18px;">
                  <p style="margin:0 0 8px;font-size:14px;line-height:22px;color:#9a3412;"><strong>Importante</strong></p>
                  <p style="margin:0;font-size:14px;line-height:22px;color:#9a3412;">
                    Esta carteira possui finalidade educacional e nao constitui recomendacao oficial de investimento.
                    Sempre considere sua situacao financeira antes de investir.
                  </p>
                </div>
              </td>
            </tr>
            <tr>
              <td style="border-top:1px solid #e2e8f0;padding:20px 24px;text-align:center;background-color:#ffffff;">
                <p style="margin:0;font-size:13px;line-height:22px;color:#64748b;">
                  <strong>Finance Predict</strong><br>
                  Sistema Inteligente de Recomendacao de Investimentos<br>
                  Trabalho de Conclusao de Curso<br>
                  {current_year}
                </p>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>
""".strip()


def _format_money(value):
    amount = float(value or 0)
    return f"R$ {amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
