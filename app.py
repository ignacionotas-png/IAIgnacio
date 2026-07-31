import streamlit as st
import os
from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_experimental.utilities import PythonREPL
from langchain.agents import initialize_agent, Tool, AgentType

st.set_page_config(page_title="Mi IA Privada", page_icon="🤖")
st.title("🤖 Mi Gemini Personal")

# Configuración de herramientas
llm = ChatGroq(api_key=st.secrets["GROQ_API_KEY"], model_name="llama3-70b-8192")
search = TavilySearchResults(api_key=st.secrets["TAVILY_API_KEY"])
python_repl = PythonREPL()

tools = [
    Tool(name="Buscador", func=search.run, description="Busca en internet"),
    Tool(name="Calculadora", func=python_repl.run, description="Resuelve matemáticas")
]

agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION)

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if p := st.chat_input("Pregunta algo..."):
    st.session_state.messages.append({"role": "user", "content": p})
    with st.chat_message("user"): st.markdown(p)
    with st.chat_message("assistant"):
        r = agent.run(p)
        st.markdown(r)
        st.session_state.messages.append({"role": "assistant", "content": r})
