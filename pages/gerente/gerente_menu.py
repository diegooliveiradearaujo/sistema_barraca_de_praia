import streamlit as st
from pages.gerente.funcionario_gerenciamento import cadastrar_funcionario
from pages.gerente.pedido import listar_pedidos
from pages.gerente.mesa import adicionar_mesa
from pages.gerente.produto import adicionar_editar_produto


st.sidebar.image("img/logo.png", use_container_width=True)

# menu gerente
opcao = st.sidebar.selectbox(
    "Menu",
    [
        "Funcionários",
        "Mesas",
        "Produtos",
        "Pedidos"
    ]
)

# navegação
if opcao == "Funcionários":
    cadastrar_funcionario()

elif opcao == "Mesas":
    adicionar_mesa()

elif opcao == "Produtos":
    adicionar_editar_produto()

elif opcao == "Pedidos":
    listar_pedidos()