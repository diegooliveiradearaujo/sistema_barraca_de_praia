import streamlit as st
from db import conectar


# busca mesas
def buscar_mesas():

    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        SELECT numero
        FROM mesas
        ORDER BY numero
    """)

    dados = cur.fetchall()

    cur.close()
    conn.close()

    return [{"numero": m[0]} for m in dados]


# verifica se mesa existe
def mesa_existe(numero):

    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        SELECT 1
        FROM mesas
        WHERE numero = %s
    """, (numero,))

    existe = cur.fetchone()

    cur.close()
    conn.close()

    return existe is not None


# salva mesa
def salvar_mesa(numero):

    conn = conectar()
    cur = conn.cursor()

    descricao = f"Mesa {numero}"

    cur.execute("""
        INSERT INTO mesas (numero, descricao)
        VALUES (%s, %s)
    """, (numero, descricao))

    conn.commit()

    cur.close()
    conn.close()


# lista mesas
def listar_mesas(mesas):

    st.subheader("Mesas do restaurante")

    if len(mesas) == 0:
        st.write("Nenhuma mesa cadastrada")
        return

    for m in mesas:

        col1, col2 = st.columns([4, 1])

        with col1:
            st.write(f"Mesa {m['numero']}")

        with col2:
            st.button("🗑️", key=f"delete_{m['numero']}")


# adiciona mesa
def adicionar_mesa():

    st.title("🪑 Gerenciamento de Mesas")

    st.divider()

    # mensagem flash - sucesso ou warning
    if "mensagem" not in st.session_state:
        st.session_state.mensagem = None

    if st.session_state.mensagem:
        tipo, texto = st.session_state.mensagem

        if tipo == "success":
            st.success(texto)
        elif tipo == "warning":
            st.warning(texto)

        st.session_state.mensagem = None


    if "nova_mesa" not in st.session_state:
        st.session_state.nova_mesa = 1

    st.subheader("Adicionar mesa")

    numero = st.number_input(
        "Número da mesa",
        min_value=1,
        step=1,
        key="nova_mesa"
    )

    # botão adicionar mesa
    if st.button("Adicionar mesa"):

        numero_int = int(numero)

        if mesa_existe(numero_int):

            st.session_state.mensagem = ("warning", "Mesa já existe!")

        else:

            salvar_mesa(numero_int)

            st.session_state.mensagem = ("success", "Mesa adicionada!")

            # limpa campo corretamente
            if "nova_mesa" in st.session_state:
                del st.session_state["nova_mesa"]

        st.rerun()

    st.divider()

    mesas = buscar_mesas()

    listar_mesas(mesas)

# executa a página
adicionar_mesa()