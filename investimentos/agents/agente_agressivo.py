from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.agents import initialize_agent, AgentType
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import Tool
from decouple import config

from investimentos.models import Investimento


model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=config("GEMINI_API_KEY")
)



def busca_investimentos_agressivos(_input: str):
    investimentos = Investimento.objects.filter(risco__in=[3, 4, 5])

    return [
        {
            "nome": i.nome,
            "risco": i.risco
        }
        for i in investimentos
    ]


def agente_agressivo(cliente):

    if cliente.tipo_de_investidor.lower() != "agressivo":
        return "Este agente é exclusivo para investidores agressivos."

    aporte = float(cliente.aporte_mensal)

    tool = Tool(
        name="busca_investimentos_agressivos",
        func=busca_investimentos_agressivos,
        description="Retorna somente investimentos do banco"
    )

    agent = initialize_agent(
        tools=[tool],
        llm=model,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True
    )

    prompt = f"""
Você é um agente de investimentos.

REGRAS OBRIGATÓRIAS:
- Só use dados da tool
- Explique de forma simplificada
- NÃO invente investimentos
- NÃO escreva texto longo

O usuário tem aporte mensal de R$ {aporte}

Tarefa:
- distribuir o aporte entre os melhores ativos de risco alto

FORMATO:

Nome do ativo - Valor investido
"""

    response = agent.invoke(prompt)

    return response["output"]