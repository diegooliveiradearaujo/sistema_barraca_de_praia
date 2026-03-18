import streamlit as st
from auth import autenticar

st.set_page_config(page_title="Barraca Latinos", page_icon="🏖️", layout="centered")

# Verifica se a variável "logado" ainda não existe no session_state (primeiro acesso do usuário).
# Se não existir, inicializa como False (usuário não está logado).
if "logado" not in st.session_state:
    st.session_state.logado = False

# login
if not st.session_state.logado:

    col1, col2, col3 = st.columns([1,3,1])

    with col2:
        st.image("img\logo.png", width=350)
    col1, col2, col3 = st.columns([1,2,1])

    with col2:
        st.title("Login")

        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            user = autenticar(usuario, senha)

            if user:
                st.session_state.logado = True
                st.session_state.usuario = user[0]
                st.session_state.tipo = user[1]

                st.rerun()

            else:
                st.error("Usuário ou senha inválidos")

else:

    # navegação
    if st.session_state.tipo == "gerente":
        pg = st.navigation([
            st.Page("pages/gerente/gerente_menu.py", title="Gerente")
        ])

    elif st.session_state.tipo == "funcionario":
        pg = st.navigation([
            st.Page("pages/funcionario/funcionario_pedido.py", title="Pedidos")
        ])

    else:
        st.error("Tipo de usuário inválido")
        st.stop()

    pg.run()