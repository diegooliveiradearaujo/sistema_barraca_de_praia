import streamlit as st
from datetime import datetime
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

    return [m[0] for m in dados]


# busca produtos
def buscar_produtos():

    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        SELECT nome, valor
        FROM produtos
        ORDER BY nome
    """)

    dados = cur.fetchall()

    cur.close()
    conn.close()

    return {p[0]: p[1] for p in dados}


# contador controle pedido/atendimento
def descobrir_contador(mesa, funcionario):

    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        SELECT contador_pedido_vez, flag_fim_atendimento
        FROM pedidos
        WHERE mesa = %s
        AND funcionario = %s
        ORDER BY data DESC
        LIMIT 1
    """, (mesa, funcionario))

    ultimo = cur.fetchone()

    if ultimo is None:
        contador = 1
    else:
        contador_atual, flag_fim = ultimo

        if flag_fim:
            contador = contador_atual + 1
        else:
            contador = contador_atual

    cur.close()
    conn.close()

    return contador


# adiciona pedido
def adicionar_pedido(mesa, funcionario, produto, quantidade, valor_unitario):

    contador = descobrir_contador(mesa, funcionario)

    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO pedidos
        (mesa, data, funcionario, produto, quantidade, valor_unitario,
         flag_cancelamento, flag_fim_atendimento, contador_pedido_vez)
        VALUES (%s,%s,%s,%s,%s,%s,FALSE,FALSE,%s)
    """,
    (
        mesa,
        datetime.now(),
        funcionario,
        produto,
        quantidade,
        valor_unitario,
        contador
    ))

    conn.commit()

    cur.close()
    conn.close()


# finaliza mesa
def finalizar_mesa(mesa, funcionario):

    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        UPDATE pedidos
        SET flag_fim_atendimento = TRUE,
            data = %s
        WHERE id = (
            SELECT id
            FROM pedidos
            WHERE mesa = %s
            AND funcionario = %s
            ORDER BY data DESC
            LIMIT 1
        )
    """, (datetime.now(), mesa, funcionario))

    conn.commit()

    cur.close()
    conn.close()


# limpa campos de preenchimento
def limpar_campos():
    for campo in ["mesa", "produto", "quantidade"]:
        if campo in st.session_state:
            del st.session_state[campo]


# registro de pedido
def registro_pedido():

    st.title("Registrar Pedido")

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

    # info do funcionario logado
    funcionario = st.session_state.get("usuario", "Funcionário")

    st.write(f"Funcionário: **{funcionario}**")

    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    st.write(f"Data/Hora: **{agora}**")

    st.divider()

    mesas = buscar_mesas()
    produtos = buscar_produtos()

    # estados iniciais
    if "mesa" not in st.session_state:
        st.session_state.mesa = None

    if "produto" not in st.session_state:
        st.session_state.produto = None

    if "quantidade" not in st.session_state:
        st.session_state.quantidade = 1

    # formulario
    mesa = st.selectbox(
        "Mesa",
        options=[None] + mesas,
        key="mesa"
    )

    produto = st.selectbox(
        "Produto",
        options=[None] + list(produtos.keys()),
        key="produto"
    )

    if produto:
        valor_unitario = produtos[produto]
        st.write(f"Valor unitário: **R${valor_unitario:.2f}**")
    else:
        valor_unitario = 0

    quantidade = st.number_input(
        "Quantidade",
        min_value=1,
        step=1,
        key="quantidade"
    )

    total = quantidade * valor_unitario
    st.write(f"Total: **R${total:.2f}**")

    st.divider()

    col1, col2 = st.columns(2)

    # adicionar pedido
    with col1:

        if st.button("Adicionar pedido"):

            if mesa and produto:

                adicionar_pedido(
                    mesa,
                    funcionario,
                    produto,
                    quantidade,
                    valor_unitario
                )

                st.session_state.mensagem = ("success", "Pedido adicionado!")

                limpar_campos()
                st.rerun()

            else:
                st.session_state.mensagem = ("warning", "Selecione mesa e produto.")
                st.rerun()

    # botao finalizar mesa
    with col2:

        if st.button("Finalizar mesa"):

            if mesa:

                finalizar_mesa(mesa, funcionario)

                st.session_state.mensagem = ("success", "Mesa finalizada!")

                limpar_campos()
                st.rerun()

            else:
                st.session_state.mensagem = ("warning", "Selecione uma mesa.")
                st.rerun()


registro_pedido()