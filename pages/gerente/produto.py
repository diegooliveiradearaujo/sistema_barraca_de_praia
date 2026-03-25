import streamlit as st
from db import conectar

# busca produtos
def buscar_produtos(filtro=""):

    conn = conectar()
    cur = conn.cursor()

    if filtro:
        cur.execute("""
            SELECT id, nome, valor, categoria
            FROM produtos
            WHERE LOWER(nome) LIKE LOWER(%s)
            ORDER BY nome
        """, (f"%{filtro}%",))
    else:
        cur.execute("""
            SELECT id, nome, valor, categoria
            FROM produtos
            ORDER BY nome
        """)

    dados = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {"id": p[0], "nome": p[1], "valor": p[2], "categoria": p[3]}
        for p in dados
    ]


# verifica se produto existe
def produto_existe(nome):

    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        SELECT 1
        FROM produtos
        WHERE LOWER(nome) = LOWER(%s)
    """, (nome.strip(),))

    existe = cur.fetchone()

    cur.close()
    conn.close()

    return existe is not None


# adiciona produto
def adicionar_produto(nome, valor, categoria):

    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO produtos (nome, valor, categoria)
        VALUES (%s, %s, %s)
    """, (nome.strip(), valor, categoria))

    conn.commit()

    cur.close()
    conn.close()


# edita produto
def editar_produto(id_produto, nome, valor, categoria):

    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        UPDATE produtos
        SET nome=%s, valor=%s, categoria=%s
        WHERE id=%s
    """, (nome.strip(), valor, categoria, id_produto))

    conn.commit()

    cur.close()
    conn.close()


# deleta produto
def deletar_produto(id_produto):

    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM produtos
        WHERE id=%s
    """, (id_produto,))

    conn.commit()

    cur.close()
    conn.close()


# lista produto
def listar_produtos(produtos):

    st.subheader("Produtos disponíveis")

    if len(produtos) == 0:
        st.write("Nenhum produto cadastrado")
        return

    for p in produtos:

        col1, col2, col3, col4, col5 = st.columns([3,2,2,1,1])

        with col1:
            st.write(p["nome"])

        with col2:
            st.write(p["categoria"])

        with col3:
            st.write(f"R$ {p['valor']:.2f}")

        with col4:
            if st.button("🔧", key=f"edit_{p['id']}"):
                st.session_state.editar_produto = p
                popup_edicao()

        with col5:
            if st.button("🗑️", key=f"del_{p['id']}"):
                deletar_produto(p["id"])
                st.rerun()


# edita produto (popup)
@st.dialog("Editar produto")
def popup_edicao():

    if "editar_produto" not in st.session_state:
        st.warning("Nenhum produto selecionado")
        return

    produto = st.session_state.editar_produto

    nome = st.text_input("Produto", value=produto["nome"])

    valor = st.number_input(
        "Valor unitário (R$)",
        min_value=0.0,
        value=float(produto["valor"])
    )

    categoria = st.selectbox(
        "Categoria",
        ["Bebida", "Comida"],
        index=0 if produto["categoria"] == "Bebida" else 1
    )

    if st.button("Salvar alterações"):

        editar_produto(produto["id"], nome, valor, categoria)

        del st.session_state.editar_produto

        st.success("Produto atualizado!")
        st.rerun()


# adiciona edita produto
def adicionar_editar_produto():

    st.title("🍽️Gerenciamento de Produtos")

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

    st.divider()
    st.subheader("Adicionar produto")

    # estados iniciais
    if "novo_nome" not in st.session_state:
        st.session_state.novo_nome = ""

    if "novo_valor" not in st.session_state:
        st.session_state.novo_valor = 0.0

    if "nova_categoria" not in st.session_state:
        st.session_state.nova_categoria = None

    if "limpar_form" not in st.session_state:
        st.session_state.limpar_form = False

    # limpar formulário antes de renderizar
    if st.session_state.limpar_form:
        st.session_state.novo_nome = ""
        st.session_state.novo_valor = 0.0
        st.session_state.nova_categoria = None
        st.session_state.limpar_form = False

    # formulário
    nome = st.text_input("Produto", key="novo_nome")

    valor = st.number_input(
        "Valor unitário (R$)",
        min_value=0.0,
        key="novo_valor"
    )

    categoria = st.radio(
        "Categoria",
        ["Bebida", "Comida"],
        index=None,
        key="nova_categoria"
    )

    formulario_valido = (
        nome.strip() != "" and
        categoria is not None
    )

    # botão adicionar produto
    if st.button("Adicionar produto", disabled=not formulario_valido):

        if produto_existe(nome):

            st.session_state.mensagem = ("warning", "Produto já existe!")

        else:

            adicionar_produto(nome, valor, categoria)

            st.session_state.mensagem = ("success", "Produto adicionado!")

            st.session_state.limpar_form = True

        st.rerun()

    st.divider()

    # listagem
    filtro = st.text_input("Filtrar produto por nome")

    produtos = buscar_produtos(filtro)

    listar_produtos(produtos)

# executa a página
adicionar_editar_produto()