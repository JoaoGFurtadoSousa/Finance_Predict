from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.agent_toolkits import ini
from decouple import config

# =========================
# MODEL
# =========================
model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=config("GEMINI_API_KEY")
)

# =========================
# TOOL (CORRETO)
# =========================
search = DuckDuckGoSearchRun()

tools = [
    Tool(
        name="search_etf",
        func=search.run,
        description="Busca ETFs negociados na B3 e informações financeiras"
    )
]

# =========================
# AGENT (ESTÁVEL NA SUA VERSÃO)
# =========================
agent = initialize_agent(
    tools=tools,
    llm=model,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# =========================
# EXECUÇÃO
# =========================
response = agent.invoke({
    "input": "Quais ETFs da B3 são bons para investidor conservador?"
})

print(response["output"])