import streamlit as st
from groq import Groq
from tavily import TavilyClient
import json

# Configuración de la página
st.set_page_config(page_title="Mi IA Privada", page_icon="🤖")
st.title("🤖 Mi Gemini Personal")

# Inicializar Clientes
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
tavily = TavilyClient(api_key=st.secrets["TAVILY_API_KEY"])

# Definición de herramientas para la IA
def buscar_en_web(query):
    return tavily.search(query=query)["results"]

def calcular(operacion):
    try:
        # Esto permite resolver cualquier cuenta matemática en Python
        return str(eval(operacion, {"__builtins__": None}, {"abs": abs, "pow": pow}))
    except:
        return "Error en el cálculo"

# Configuración del historial
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("¿En qué puedo ayudarte?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # 1. Enviar pregunta a Groq
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "buscar_en_web",
                        "description": "Busca información actual en internet",
                        "parameters": {"type": "object", "properties": {"query": {"type": "string"}}}
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "calcular",
                        "description": "Resuelve operaciones matemáticas",
                        "parameters": {"type": "object", "properties": {"operacion": {"type": "string"}}}
                    }
                }
            ]
        )

        msg = response.choices[0].message
        
        # 2. Verificar si la IA quiere usar una herramienta
        if msg.tool_calls:
            for tool_call in msg.tool_calls:
                func_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                
                if func_name == "buscar_en_web":
                    res = buscar_en_web(args['query'])
                else:
                    res = calcular(args['operacion'])
                
                # Pedir a la IA que redacte la respuesta final con los datos obtenidos
                final_res = client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[
                        {"role": "user", "content": prompt},
                        msg,
                        {"role": "tool", "tool_call_id": tool_call.id, "content": str(res)}
                    ]
                )
                answer = final_res.choices[0].message.content
        else:
            answer = msg.content

        st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
