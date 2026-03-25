import streamlit as st
from datetime import date
from db import conectar

# cadastra funcionário
def cadastrar_funcionario():   
    st.title("👨‍🍳Gerenciamento de Funcionários")

    st.divider()

    st.subheader("Cadastrar funcionário")

    nome = st.text_input("Nome completo")
    data = st.date_input("Data cadastro", value=date.today())

    if st.button("Adicionar funcionário"):

        conn = conectar()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO funcionarios (nome, data_cadastro)
            VALUES (%s,%s)
            """,
            (nome, data)
        )

        conn.commit()
        cur.close()
        conn.close()
        
        st.success("Funcionário adicionado!")

    conn = conectar()
    cur = conn.cursor()

    cur.execute("SELECT nome, data_cadastro FROM funcionarios")
    dados = cur.fetchall()

    st.divider()

    st.subheader("Funcionários cadastrados")

    for f in dados:
        st.write(f"{f[0]} - {f[1]}")

    cur.close()
    conn.close()


# executa a página
cadastrar_funcionario()