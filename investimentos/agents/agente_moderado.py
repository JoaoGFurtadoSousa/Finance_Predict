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





def busca_investimentos_moderados(_input: str):
    investimentos = Investimento.objects.filter(risco__in=[2, 3])

    resultado = []
    for i in investimentos:
        resultado.append(f"{i.nome} | risco {i.risco}")

    return "\n".join(resultado)


def agente_moderado(cliente):

    if cliente.tipo_de_investidor.lower() != "moderado":
        return "Este agente é exclusivo para investidores moderados."

    aporte = float(cliente.aporte_mensal)

    tool_investimentos = Tool(
        name="busca_investimentos_moderados",
        func=busca_investimentos_moderados,
        description="Busca investimentos moderados (risco 2 e 3) do banco"
    )

    tools = [tool_investimentos]

    agent = initialize_agent(
    tools=tools,
    llm=model,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True
)

    prompt_template = PromptTemplate.from_template(
        """
Você é um consultor de investimentos para iniciantes.

O usuário é MODERADO, ou seja, aceita risco médio para buscar melhores retornos.

Aporte mensal: R$ {aporte}

Sua tarefa:
1. Use a tool para buscar investimentos moderados
2. Montar uma carteira equilibrada
3. Misturar segurança e crescimento
4. Explicar de forma simples
5. Evitar termos técnicos

Regras:
- Parte do dinheiro deve estar em segurança
- Parte deve buscar crescimento
- Nada muito arriscado

Formato:
- Explicação simples
- Carteira sugerida
- Valores por investimento
"""
    )

    prompt = prompt_template.format(aporte=aporte)

    response = agent.invoke(prompt)

    return response["output"]