from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_classic.agents import initialize_agent, AgentType
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import Tool
from decouple import config


model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=config("GEMINI_API_KEY"))

tools = [DuckDuckGoSearchRun()]

agent = initialize_agent(tools= tools,
                         llm= model,
                         agent= AgentType.ZERO_SHOT_REACT_DESCRIPTION)

prompt_template = PromptTemplate.from_template(
    template = '''Pesquise sobre o ETF {etf} e fale qual é o valor de mercado atual.'''
)

prompt = prompt_template.format(etf = 'BOVA11')

response = agent.invoke(prompt)
print(response)