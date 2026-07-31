import streamlit as st
import os
from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_experimental.utilities import PythonREPL
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import Tool

# Configuración de página
st.set_page_config(page_title="Mi IA Privada", page_icon="🤖")
st.title("🤖 Mi Gemini Personal")

# 1. Herramientas
search = TavilySearchResults(api_key=st.secrets["TAVILY_API_KEY"])
python_repl = PythonREPL()

tools = [
    Tool(
        name="Buscador",
        func=search.run,
        description="Busca información actual en internet."
    ),
    Tool(
        name="Calculadora",
        func=python_repl.run,
        description="Resuelve problemas matemáticos usando Python."
    )
]

# 2. Cerebro (Groq)
llm = ChatGroq(
    api_key=st.secrets["GROQ_API_KEY"],
    model_name="llama3-70b-8192",
    temperature=0
)

# 3. Prompt moderno y compatible
prompt = ChatPromptTemplate.from_messages([
    ("system", "Eres un asistente con acceso a buscador y calculadora. Responde siempre en español."),
    ("placeholder", "{chat_history}"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

# Intentamos crear el agente con un método alternativo muy estable
try:
    from langchain.agents import create_tool_calling_agent
    agent = create_tool_calling_agent(llm, tools, prompt)
except ImportError:
    # Si falla el anterior, usamos el de OpenAI Tools que Groq también entiende
    agent = create_openai_tools_agent(llm, tools, prompt)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# 4. Interfaz de Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if p := st.chat_input("Escribe tu duda aquí..."):
    st.session_state.messages.append({"role": "user", "content": p})
    with st.chat_message("user"):
        st.markdown(p)
    
    with st.chat_message("assistant"):
        try:
            # Ejecutamos la consulta
            response = agent_executor.invoke({"input": p})["output"]
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"Error al procesar: {str(e)}")
