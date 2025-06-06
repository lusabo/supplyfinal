import asyncio
import streamlit as st
from dotenv import load_dotenv
from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp

load_dotenv()

# ----------------------------------------------------------------------
# 🌐 Conexão com o servidor MCP
# ----------------------------------------------------------------------
mcp_server = MCPServerStreamableHttp({"url": "http://localhost:8000/mcp"})

# ----------------------------------------------------------------------
# 🤖 Definição do agente
# ----------------------------------------------------------------------

agente_compras = Agent(
    name="AssistenteCompras",
    # Instruções iniciais do agente (prompt do sistema)
    instructions="""
        Você é um assistente de compras que auxilia no processo de solicitação de propostas. 
        Você pode buscar fornecedores em um banco de dados, enviar solicitações por e-mail,
        ler respostas e recomendar a melhor proposta. Responda de forma clara e peça confirmação 
        ao usuário antes de ações críticas.
    """,
    model="gpt-4o-mini",
    mcp_servers=[mcp_server]
)

# ----------------------------------------------------------------------
# 🔄 Função assíncrona para perguntar ao agente
# ----------------------------------------------------------------------
async def ask_agent(question: str) -> str:
    await mcp_server.connect()
    result = await Runner.run(agente_compras, question)
    return result.final_output

# ----------------------------------------------------------------------
# 🎨 Interface Streamlit
# ----------------------------------------------------------------------

st.title("Assistente de Compras - Chat")
st.markdown("Converse com o assistente para criar solicitações de compra e gerenciar propostas.")

# Estado da conversa armazenado na sessão (histórico de mensagens)
if "history" not in st.session_state:
    st.session_state.history = []  # lista de (role, message)

# Caixa de entrada do usuário
entrada = st.chat_input("Digite sua mensagem:")
if entrada:
    # Exibe imediatamente a mensagem do usuário na interface
    st.session_state.history.append(("user", entrada))
    # Chama o agente da OpenAI para obter a resposta
    resultado = asyncio.run(ask_agent(entrada))  # executa a função assíncrona    
    # Armazena e exibe a resposta do assistente
    st.session_state.history.append(("assistant", resultado))

# Renderiza o histórico de mensagens na tela
for role, msg in st.session_state.history:
    with st.chat_message(role):
        st.write(msg)