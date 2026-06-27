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



def busca_investimentos_conservadores(_input: str):
    investimentos = Investimento.objects.filter(risco__in=[1, 2])

    resultado = []
    for i in investimentos:
        resultado.append(
            f"{i.nome} | risco {i.risco}"
        )

    return "\n".join(resultado)



def agente_conservador(cliente):


    if cliente.tipo_de_investidor.lower() != "conservador":
        return "Este agente é exclusivo para investidores conservadores."

    aporte = float(cliente.aporte_mensal)
    

    tool_investimentos = Tool(
        name="busca_investimentos_conservadores",
        func=busca_investimentos_conservadores,
        description="Busca investimentos conservadores (risco 1 e 2) do banco"
    )

    tools = [tool_investimentos]

  
    agent = initialize_agent(
        tools=tools,
        llm=model,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True
    )

    # 4. prompt estruturado
    prompt_template = PromptTemplate.from_template(
"""
Você é um agente que deve obrigatoriamente seguir o formato ReAct.

Você possui acesso à ferramenta:
busca_investimentos_conservadores

Sempre utilize o seguinte formato:

Thought: descreva o que você pretende fazer
Action: busca_investimentos_conservadores
Action Input: investimentos conservadores
Observation: resultado da ferramenta

Quando terminar utilize:

Final Answer:
Resumo da estratégia

Carteira recomendada:
- Nome do investimento
- Valor recomendado para investir
- Motivo da escolha

Total investido: R$ {aporte}

DADOS DO CLIENTE

Perfil: Conservador
Aporte: R$ {aporte}
Reserva de emergência: {reserva_de_emergencia}
Valor da reserva: {valor_armazenado_reserva_emergencia}
Tolerância à volatilidade: {tolerancia_volatilidade}
Experiência: {experiencia_em_investimentos}
Perda máxima aceitável: {aceitacao_perda_percentual}
Liquidez necessária: {liquidez_necessaria}
Prazo esperado: {tempo_estimado_retorno}

IMPORTANTE:
- Utilize apenas investimentos retornados pela ferramenta.
- Nunca invente investimentos.
- Nunca pesquise na internet.
"""
)
    prompt = prompt_template.format(aporte=aporte, 
                                    reserva_de_emergencia = cliente.reserva_de_emergencia,
                                    valor_armazenado_reserva_emergencia = cliente.valor_armazenado_reserva_emergencia,
                                    tolerancia_volatilidade= cliente.tolerancia_volatilidade,
                                    experiencia_em_investimentos= cliente.experiencia_em_investimentos,
                                    aceitacao_perda_percentual= cliente.aceitacao_perda_percentual,
                                    liquidez_necessaria= cliente.liquidez_necessaria,
                                    tempo_estimado_retorno= cliente.tempo_estimado_retorno)

    # 5. execução
    response = agent.invoke(prompt)

    portfolio_text = response["output"]
    audit_result = audit_recommendation(cliente, portfolio_text)
    if audit_result["status"] == "approved":
        safe_send_portfolio_email(cliente, portfolio_text)
        return portfolio_text
    return f"{portfolio_text}\n\n{audit_result['message']}"
