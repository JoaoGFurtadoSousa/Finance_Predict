from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.agents import initialize_agent, AgentType
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import Tool
from decouple import config

from clients.services.email_service import safe_send_portfolio_email
from investimentos.models import Investimento
from investimentos.services.recommendation_audit_skill import audit_recommendation


model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=config("GEMINI_API_KEY")
)



def busca_investimentos_moderados(_input: str):
    investimentos = Investimento.objects.filter(risco__in=[2, 3])

    return [
        {
            "nome": i.nome,
            "risco": i.risco
        }
        for i in investimentos
    ]


def agente_moderado(cliente):

    if cliente.tipo_de_investidor.lower() != "moderado":
        return "Este agente é exclusivo para investidores moderados."

    aporte = float(cliente.aporte_mensal)

    tool = Tool(
        name="busca_investimentos_agressivos",
        func=busca_investimentos_moderados,
        description="Retorna somente investimentos do banco"
    )

    agent = initialize_agent(
        tools=[tool],
        llm=model,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True
    )

    prompt_template = PromptTemplate.from_template(
    """Você é um agente que deve obrigatoriamente seguir o formato ReAct.

Você possui acesso à ferramenta:
busca_investimentos_moderados

Sempre utilize o seguinte formato:

Thought: descreva o que você pretende fazer

Action: busca_investimentos_moderados

Action Input: investimentos moderados

Observation: resultado da ferramenta

Quando terminar utilize:

Final Answer:

Resumo da estratégia

Carteira recomendada:

Nome do investimento
Valor recomendado para investir
Motivo da escolha

Total investido: R$ {aporte}

DADOS DO CLIENTE

Perfil: Moderado

Aporte: R$ {aporte}

Reserva de emergência:
{reserva_de_emergencia}

Valor da reserva:
{valor_armazenado_reserva_emergencia}

Tolerância à volatilidade:
{tolerancia_volatilidade}

Experiência em investimentos:
{experiencia_em_investimentos}

Perda máxima aceitável:
{aceitacao_perda_percentual}

Liquidez necessária:
{liquidez_necessaria}

Prazo esperado para retorno:
{tempo_estimado_retorno}

IMPORTANTE:

Utilize apenas investimentos retornados pela ferramenta.
Nunca invente investimentos.
Nunca pesquise na internet.
Priorize investimentos de risco 2 e 3.
Pode utilizar uma pequena parcela de ativos de risco 4 caso sejam compatíveis com o perfil do cliente.
Busque equilíbrio entre segurança e crescimento patrimonial.
Diversifique entre renda fixa, ETFs globais, ETFs de índice e fundos imobiliários quando possível.
Distribua 100% do aporte mensal.
Evite concentração excessiva em um único ativo.
Considere liquidez, volatilidade, rentabilidade e horizonte de investimento.
Explique de forma simples para investidores iniciantes."""
    )
    
    prompt = prompt_template.format(aporte=aporte, 
                                    reserva_de_emergencia = cliente.reserva_de_emergencia,
                                    valor_armazenado_reserva_emergencia = cliente.valor_armazenado_reserva_emergencia,
                                    tolerancia_volatilidade= cliente.tolerancia_volatilidade,
                                    experiencia_em_investimentos= cliente.experiencia_em_investimentos,
                                    aceitacao_perda_percentual= cliente.aceitacao_perda_percentual,
                                    liquidez_necessaria= cliente.liquidez_necessaria,
                                    tempo_estimado_retorno= cliente.tempo_estimado_retorno)

    response = agent.invoke(prompt)

    portfolio_text = response["output"]
    audit_result = audit_recommendation(cliente, portfolio_text)
    if audit_result["status"] == "approved":
        safe_send_portfolio_email(cliente, portfolio_text)
        return portfolio_text
    return f"{portfolio_text}\n\n{audit_result['message']}"
