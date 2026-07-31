import streamlit as st
import os

# Importaciones directas para evitar errores de versión
from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_experimental.utilities import PythonREPL
from langchain.agents.agent import AgentExecutor
from langchain.agents.openai_tools.base import create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import Tool

# Configuración visual estilo oscuro
st.set_page_config(page_title="Mi IA Privada", page_icon="🤖")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .stChatMessage { border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 Mi Gemini Personal")

# 1. Configurar Herramientas
try:
    search = TavilySearchResults(api_key=st.secrets["TAVILY_API_KEY"])
    python_repl = PythonREPL()

    tools = [
        Tool(name="Buscador", func=search.run, description="Busca en internet"),
        Tool(name="Calculadora", func=python_repl.run, description="Resuelve matemáticas con Python")
    ]

    # 2. Configurar Cerebro
    llm = ChatGroq(
        api_key=st.secrets["GROQ_API_KEY"],
        model_name="llama3-70b-8192",
        temperature=0
    )

    # 3. Prompt de Sistema
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Eres un asistente útil con acceso a internet y calculadora. Responde en español."),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    # 4. Crear el Agente
    agent = create_openai_tools_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

    # 5. Interfaz de Chat
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if p := st.chat_input("¿En qué puedo ayudarte?"):
        st.session_state.messages.append({"role": "user", "content": p})
        with st.chat_message("user"):
            st.markdown(p)
        
        with st.chat_message("assistant"):
            response = agent_executor.invoke({"input": p})["output"]
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

except Exception as e:
    st.error(f"Error de configuración: {e}")
    st.info("Asegúrate de que tus Secrets (GROQ_API_KEY y TAVILY_API_KEY) estén bien configurados.")
