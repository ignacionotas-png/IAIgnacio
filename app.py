import streamlit as st
import os

# --- TRUCO DE COMPATIBILIDAD ---
# Intentamos importar AgentExecutor de varias formas posibles
try:
    from langchain.agents import AgentExecutor
except ImportError:
    try:
        from langchain.agents.agent import AgentExecutor
    except ImportError:
        from langchain.agents.executor import AgentExecutor

try:
    from langchain.agents import create_tool_calling_agent
except ImportError:
    from langchain.agents.tool_calling_agent.base import create_tool_calling_agent

from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_experimental.utilities import PythonREPL
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import Tool

# Configuración de página
st.set_page_config(page_title="Mi IA Privada", page_icon="🤖")
st.title("🤖 Mi Gemini Personal")

# 1. Configurar Herramientas
try:
    search = TavilySearchResults(api_key=st.secrets["TAVILY_API_KEY"])
    python_repl = PythonREPL()

    tools = [
        Tool(name="Buscador", func=search.run, description="Busca en internet información actual."),
        Tool(name="Calculadora", func=python_repl.run, description="Resuelve problemas matemáticos con código Python.")
    ]

    # 2. Configurar Cerebro
    llm = ChatGroq(
        api_key=st.secrets["GROQ_API_KEY"],
        model_name="llama3-70b-8192",
        temperature=0
    )

    # 3. Prompt de Sistema
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Eres un asistente útil con acceso a internet y calculadora. Responde siempre en español."),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    # 4. Crear el Agente y el Ejecutor
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    # 5. Interfaz de Chat
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if p := st.chat_input("¿En qué puedo ayudarte hoy?"):
        st.session_state.messages.append({"role": "user", "content": p})
        with st.chat_message("user"):
            st.markdown(p)
        
        with st.chat_message("assistant"):
            # Ejecutamos el agente
            response = agent_executor.invoke({"input": p})["output"]
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

except Exception as e:
    st.error(f"Error de inicio: {e}")
    st.info("Revisa tus Secrets en la configuración de Streamlit.")
