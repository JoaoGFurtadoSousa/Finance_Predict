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

    prompt_template = PromptTemplate.from_template(
    """
    Você é um agente que deve obrigatoriamente seguir o formato ReAct.

    Você possui acesso à ferramenta:
    busca_investimentos_agressivos

    Sempre utilize o seguinte formato:

    Thought: descreva o que você pretende fazer

    Action: busca_investimentos_agressivos

    Action Input: investimentos agressivos

    Observation: resultado da ferramenta

    Quando terminar utilize:

    Final Answer:

    Resumo da estratégia

    Carteira recomendada:

    Nome do investimento
    Valor recomendado para investir
    Motivo da escolha

    DADOS DO CLIENTE

    Perfil: Agressivo

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
    Priorize investimentos de risco 4 e 5.
    Pode utilizar investimentos de risco 3 para diversificação.
    Busque maximizar o potencial de retorno compatível com o perfil do cliente.
    Considere ETFs de tecnologia, small caps e criptoativos quando disponíveis.
    Distribua 100% do aporte mensal.
    Evite concentração excessiva em um único ativo.
    Considere liquidez, volatilidade, rentabilidade e horizonte de investimento.
    Explique de forma simples para investidores iniciantes.
    Aceite maior volatilidade quando compatível com a tolerância do cliente.
    """)

    prompt = prompt_template.format(aporte=aporte, 
                                    reserva_de_emergencia = cliente.reserva_de_emergencia,
                                    valor_armazenado_reserva_emergencia = cliente.valor_armazenado_reserva_emergencia,
                                    tolerancia_volatilidade= cliente.tolerancia_volatilidade,
                                    experiencia_em_investimentos= cliente.experiencia_em_investimentos,
                                    aceitacao_perda_percentual= cliente.aceitacao_perda_percentual,
                                    liquidez_necessaria= cliente.liquidez_necessaria,
                                    tempo_estimado_retorno= cliente.tempo_estimado_retorno)

    response = agent.invoke(prompt)

    return response["output"]