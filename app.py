import streamlit as st
import os
from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_experimental.utilities import PythonREPL
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import Tool

st.set_page_config(page_title="Mi IA Privada", page_icon="🤖")
st.title("🤖 Mi Gemini Personal")

# 1. Herramientas
try:
    search = TavilySearchResults(api_key=st.secrets["TAVILY_API_KEY"])
    python_repl = PythonREPL()
    tools = [
        Tool(name="Buscador", func=search.run, description="Busca información en internet."),
        Tool(name="Calculadora", func=python_repl.run, description="Resuelve problemas matemáticos.")
    ]

    # 2. IA
    llm = ChatGroq(api_key=st.secrets["GROQ_API_KEY"], model_name="llama3-70b-8192")

    # 3. Prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Eres un asistente con buscador y calculadora. Responde en español."),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    # 4. Agente
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    # 5. Interfaz
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if p := st.chat_input("¿En qué puedo ayudarte?"):
        st.session_state.messages.append({"role": "user", "content": p})
        with st.chat_message("user"): st.markdown(p)
        with st.chat_message("assistant"):
            response = agent_executor.invoke({"input": p})["output"]
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
except Exception as e:
    st.error(f"Error: {e}")
