import streamlit as st
import asyncio
import os
from dotenv import load_dotenv
from typing import List, Dict
from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp

load_dotenv()

# Configure the page
st.set_page_config(
    page_title="Supply Chain Assistant",
    layout="wide"
)

# Custom CSS to keep input at the top and style chat
st.markdown("""
    <style>
        .stChatInputContainer {
            position: sticky;
            top: 0;
            padding: 1rem;
            background-color: white;
            z-index: 100;
            width: 100% !important;
            border-bottom: 1px solid #ddd;
        }
        .main-chat-area {
            margin-top: 70px;
            overflow-y: auto;
            max-height: calc(100vh - 200px);
            width: 100%;
        }
    </style>
""", unsafe_allow_html=True)

# MCP server connection
mcp_server = MCPServerStreamableHttp({
    "url": "http://localhost:8000/mcp"
})

# Create supply chain agent
supply_agent = Agent(
    name="Supply Chain Assistant",
    model="gpt-4o-mini",
    mcp_servers=[mcp_server],
    instructions="""
Você é um assistente de compras que conduz o usuário, em linguagem natural, pelo processo de solicitação de orçamento de materiais e produtos industriais. Siga sempre um fluxo conversacional, guiando o usuário passo a passo, validando informações e confirmando antes de enviar orçamentos por e-mail.

Fluxo geral:
1. Identifique o produto/material e a categoria desejada.
2. Liste os fornecedores disponíveis para o item/material.
3. Pergunte para quais fornecedores o usuário deseja enviar o orçamento (todos ou escolha).
4. Solicite os detalhes necessários: quantidade, especificações, prazo para propostas e prazo de entrega.
5. Confirme as informações antes de enviar.
6. Envie o orçamento por e-mail usando a ferramenta 'send_rfq_email' e informe o número da requisição gerada.

Regras e exemplos:
- Sempre valide se o material/categoria existe antes de prosseguir.
- Se o usuário não informar todos os dados necessários, pergunte de forma objetiva e clara.
- Sempre confirme com o usuário antes de enviar o orçamento.
- Após o envio, informe claramente para quais fornecedores foi enviado e o número da requisição.

Ferramentas disponíveis:
• 'list_categories' - Lista categorias de produtos
• 'list_materials' - Lista materiais disponíveis
• 'list_suppliers' - Lista fornecedores para categoria/material
• 'list_products_by_supplier' - Lista os produtos/materiais fornecidos por um fornecedor específico.
• 'find_supplier_by_name' - Detalhes de fornecedor específico
• 'send_rfq_email' - Envia orçamento por e-mail (campos: recipient, fornecedor, categoria, material, quantidade, especificacao, prazo)

Orientações:
- Seja sempre objetivo, cordial e claro.
- Use perguntas diretas para coletar informações faltantes.
- Confirme explicitamente antes de enviar orçamentos.
- Sempre informe o número da requisição após o envio.
- Se houver erro ou informação faltante, explique de forma amigável.

Responda sempre em português.
"""
)

async def responder_mcp(history: List[Dict]) -> str:
    """Processa a conversa completa pelo Supply Chain Agent."""
    try:
        await mcp_server.connect()
        # O último item do histórico é a mensagem do usuário
        user_message = history[-1]["content"]
        # Passa todo o histórico menos a última mensagem como contexto
        result = await Runner.run(
            starting_agent=supply_agent,
            input=user_message,
            context=history[:-1]
        )
        return result.final_output
    except Exception as e:
        return f"❌ Erro: {str(e)}"

# Inicializa o histórico de mensagens
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("💬 Assistente de Compras")

# Input sempre no topo
prompt = st.chat_input("Digite sua mensagem...")

# Exibe o histórico de mensagens (estilo ChatGPT)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Processa nova mensagem
if prompt:
    # Adiciona mensagem do usuário ao histórico
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Mostra mensagem do usuário imediatamente
    with st.chat_message("user"):
        st.markdown(prompt)

    # Gera resposta do assistente com todo o histórico
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            response = asyncio.run(responder_mcp(st.session_state.messages))
            st.markdown(response)
    # Adiciona resposta ao histórico
    st.session_state.messages.append({"role": "assistant", "content": response})