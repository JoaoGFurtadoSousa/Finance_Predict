from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.agents import initialize_agent, AgentType
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import Tool
import yfinance as yf
from decouple import config


model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=config("GEMINI_API_KEY"))


def busca_valor_de_etf_brasileiro_no_yf(ticker:str):
    ticker = ticker.upper() + ".SA"
    etf = yf.Ticker(ticker)
    data = etf.history(period="1d")
    last_close = data["Close"].iloc[-1]
    return f"O último preço de fechamento do {ticker} foi {last_close:.2f}"


def busca_valor_de_cripto_no_yf(ticker:str):
    ticker = ticker.upper() + "-USD"
    etf = yf.Ticker(ticker)
    data = etf.history(period="1d")
    last_close = data["Close"].iloc[-1]
    return f"O último preço de fechamento do {ticker} foi {last_close:.2f}"



def retorna_valor_de_mercado_de_etfs_brasileiras():

    yahoo_finance_tool =  Tool(
                name="busca_valor_no_yf",
                func= busca_valor_de_etf_brasileiro_no_yf,
                description= "Busca valores de ETF dentro da plataforma da Yahoo Finance"
            )

    tools = [
            yahoo_finance_tool
            ]

    agent = initialize_agent(tools= tools,
                            llm= model,
                            agent= AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                            verbose=True)


    prompt_template = PromptTemplate.from_template(
        template = '''Pesquise sobre o {tipo_investimento} {ticker} e fale qual é o valor de mercado atual. Retorne somente o valor do ETF, nada além disso'''
    )


    prompt = prompt_template.format(
        tipo_investimento = "ETF",
        ticker = 'PETR4')


    response = agent.invoke(prompt)
    print(response['output'])



def retorna_valor_de_mercado_de_criptos():

    yahoo_finance_tool =  Tool(
                name="busca_valor_de_cripto_no_yf",
                func= busca_valor_de_cripto_no_yf,
                description= "Busca valores de Criptomoedas dentro da plataforma da Yahoo Finance"
            )

    tools = [
            yahoo_finance_tool
            ]

    agent = initialize_agent(tools= tools,
                            llm= model,
                            agent= AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                            verbose=True)


    prompt_template = PromptTemplate.from_template(
        template = '''Pesquise sobre o {tipo_investimento} {ticker} e fale qual é o valor de mercado atual. Retorne somente o valor do ETF, nada além disso'''
    )


    prompt = prompt_template.format(
        tipo_investimento = "Cripto",
        ticker = 'BTC')


    response = agent.invoke(prompt)
    print(response['output'])

if __name__ == '__main__':
    retorna_valor_de_mercado_de_etfs_brasileiras()