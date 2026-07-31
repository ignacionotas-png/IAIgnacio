import streamlit as st
import os
from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_experimental.utilities import PythonREPL
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

# Configuración de la página
st.set_page_config(page_title="Mi IA Privada", page_icon="🤖")
st.title("🤖 Mi Gemini Personal")

# 1. Configuración de herramientas
# Buscador web
search = TavilySearchResults(api_key=st.secrets["TAVILY_API_KEY"])

# Calculadora avanzada
python_repl = PythonREPL()
def run_python(code: str):
    return python_repl.run(code)

from langchain.tools import Tool
tools = [
    Tool(name="Buscador", func=search.run, description="Busca en internet información actual."),
    Tool(name="Calculadora", func=run_python, description="Resuelve problemas matemáticos ejecutando código Python.")
]

# 2. Configuración del Cerebro (Groq)
llm = ChatGroq(
    api_key=st.secrets["GROQ_API_KEY"], 
    model_name="llama3-70b-8192",
    temperature=0
)

# 3. Creación del Agente (Versión Moderna)
prompt = ChatPromptTemplate.from_messages([
    ("system", "Eres un asistente útil que tiene acceso a herramientas de búsqueda y cálculo."),
    ("placeholder", "{chat_history}"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# 4. Interfaz de Usuario (Chat)
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if p := st.chat_input("Pregunta algo o pide un cálculo..."):
    st.session_state.messages.append({"role": "user", "content": p})
    with st.chat_message("user"):
        st.markdown(p)
    
    with st.chat_message("assistant"):
        # Ejecutar el agente
        response = agent_executor.invoke({"input": p})["output"]
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
