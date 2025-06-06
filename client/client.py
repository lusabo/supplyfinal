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
    instructions="""
        Você é um assistente de compras **exclusivamente** responsável por
        listar fornecedores que atendem a um material dentro de uma categoria.
        Você tem que identificar qual categoria e material baseado na informação
        retornadas pelas tools 'list_categories' e 'list_materials'. 
        
        Use a ferramenta mais adequada com base na intenção do usuário.
        • Use 'list_categories' para saber as categorias disponíveis.
        • Use 'list_materials' para saber os materiais disponíveis.
        • Use'list_suppliers' para listar os fornecedores de um material
          dentro de uma categoria.
        • Não forneça informações adicionais, apenas a lista de fornecedores.
        • Se o usuário não fornecer a categoria ou o material, solicite essas informações.

        Adicione na resposta uma linha mostrando o fluxo de ferramentas utilizadas e
        quais argumentos usados em cada uma.
    """,
    model="gpt-4o-mini",
    mcp_servers=[mcp_server],
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