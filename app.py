import streamlit as st
from groq import Groq
from tavily import TavilyClient
import json

# Configuración de la página
st.set_page_config(page_title="Mi IA Privada", page_icon="🤖")
st.title("🤖 Mi Gemini Personal")

# Inicializar Clientes (con validación)
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    tavily = TavilyClient(api_key=st.secrets["TAVILY_API_KEY"])
except Exception as e:
    st.error("Error con las API Keys. Revisa tus Secrets.")
    st.stop()

# Definición de herramientas
def buscar_en_web(query):
    try:
        return str(tavily.search(query=query, search_depth="basic")["results"])
    except:
        return "No pude encontrar resultados en la web."

def calcular(operacion):
    try:
        # Limpiamos la operación de caracteres extraños
        operacion = operacion.replace("^", "**")
        return str(eval(operacion, {"__builtins__": None}, {"abs": abs, "pow": pow}))
    except:
        return "Error en el cálculo matemático."

# Historial de chat
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
        # Mensajes para la IA incluyendo un System Prompt
        mensajes_ia = [
            {"role": "system", "content": "Eres un asistente experto. Si te piden buscar algo actual o hacer cuentas, DEBES usar tus herramientas."},
            {"role": "user", "content": prompt}
        ]

        # Definición corregida de herramientas (con 'required')
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "buscar_en_web",
                    "description": "Busca información actualizada en internet",
                    "parameters": {
                        "type": "object",
                        "properties": {"query": {"type": "string", "description": "El término de búsqueda"}},
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calcular",
                    "description": "Resuelve operaciones matemáticas",
                    "parameters": {
                        "type": "object",
                        "properties": {"operacion": {"type": "string", "description": "La operación matemática (ej: 2+2)"}},
                        "required": ["operacion"]
                    }
                }
            }
        ]

        try:
            # 1. Primera llamada a Groq
            response = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=mensajes_ia,
                tools=tools,
                tool_choice="auto"
            )

            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            # 2. Si la IA decide usar herramientas
            if tool_calls:
                mensajes_ia.append(response_message)
                
                for tool_call in tool_calls:
                    func_name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments)
                    
                    if func_name == "buscar_en_web":
                        resultado_herramienta = buscar_en_web(args.get("query"))
                    else:
                        resultado_herramienta = calcular(args.get("operacion"))
                    
                    mensajes_ia.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": func_name,
                        "content": resultado_herramienta
                    })
                
                # Segunda llamada para procesar los datos de la herramienta
                segunda_respuesta = client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=mensajes_ia
                )
                answer = segunda_respuesta.choices[0].message.content
            else:
                answer = response_message.content

            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})

        except Exception as e:
            st.error(f"Error de comunicación: {e}")
            answer = msg.content

        st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
