import streamlit as st
from agents import Runner  # do OpenAI Agents SDK
from agent_config import agente_compras

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
    resultado = Runner.run_sync(agente_compras, entrada)  # executa o loop do agente
    resposta = resultado.final_output  # texto final gerado pelo agente
    # Armazena e exibe a resposta do assistente
    st.session_state.history.append(("assistant", resposta))

# Renderiza o histórico de mensagens na tela
for role, msg in st.session_state.history:
    with st.chat_message(role):
        st.write(msg)
