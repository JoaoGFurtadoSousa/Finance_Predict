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


# -----------------------------
# TOOL: busca investimentos no banco
# -----------------------------
def busca_investimentos_conservadores(_input: str):
    investimentos = Investimento.objects.filter(risco__in=[1, 2])

    resultado = []
    for i in investimentos:
        resultado.append(
            f"{i.nome} | risco {i.risco}"
        )

    return "\n".join(resultado)


# -----------------------------
# AGENTE CONSERVADOR
# -----------------------------
def agente_conservador(cliente):

    # 1. valida perfil
    if cliente.tipo_de_investidor.lower() != "conservador":
        return "Este agente é exclusivo para investidores conservadores."

    aporte = float(cliente.aporte_mensal)

    # 2. tools
    tool_investimentos = Tool(
        name="busca_investimentos_conservadores",
        func=busca_investimentos_conservadores,
        description="Busca investimentos conservadores (risco 1 e 2) do banco"
    )

    tools = [tool_investimentos]

    # 3. agente
    agent = initialize_agent(
        tools=tools,
        llm=model,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )

    # 4. prompt estruturado
    prompt_template = PromptTemplate.from_template(
        """
Você é um consultor de investimentos para iniciantes.

O usuário é CONSERVADOR e tem perfil de baixo risco.

Aporte mensal: R$ {aporte}

Sua tarefa:
1. Use a tool para buscar investimentos conservadores
2. Escolha os melhores investimentos de forma simples
3. Distribua o aporte mensal entre eles
4. Explique de forma muito simples, como se fosse para alguém iniciante
5. Não use linguagem técnica complexa

Formato da resposta:
- Resumo simples
- Lista de investimentos
- Quanto investir em cada um
"""
    )

    prompt = prompt_template.format(aporte=aporte)

    # 5. execução
    response = agent.invoke(prompt)

    return response["output"]