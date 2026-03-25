import streamlit as st
from datetime import date
from db import conectar

# lista pedidos realizados
def listar_pedidos():
    st.title("🧾Gerenciamento de Pedidos/Mesa")

    st.divider()

    st.subheader("Filtro para a busca")

    conn = conectar()
    cur = conn.cursor()

    # busca mesas e funcionários para filtro
    cur.execute("SELECT DISTINCT mesa FROM pedidos ORDER BY mesa")
    mesas = [m[0] for m in cur.fetchall()]
    mesas.insert(0, "Todos")

    cur.execute("SELECT DISTINCT funcionario FROM pedidos ORDER BY funcionario")
    funcionarios = [f[0] for f in cur.fetchall()]
    funcionarios.insert(0, "Todos")

    # filtros
    filtro_mesa = st.selectbox("Filtrar por mesa", mesas)
    filtro_funcionario = st.selectbox("Filtrar por funcionário", funcionarios)
    data_inicial = st.date_input("Data início", value=date.today())
    data_final = st.date_input("Data fim", value=date.today())
    
    st.divider()

    # consulta filtrada
    query = """
        SELECT mesa, data, funcionario, produto, quantidade, valor_unitario,
               total, flag_cancelamento, flag_fim_atendimento, contador_pedido_vez
        FROM pedidos
        WHERE data::date BETWEEN %s AND %s
    """
    params = [data_inicial, data_final]

    if filtro_mesa != "Todos":
        query += " AND mesa = %s"
        params.append(filtro_mesa)
    if filtro_funcionario != "Todos":
        query += " AND funcionario = %s"
        params.append(filtro_funcionario)

    query += " ORDER BY mesa, funcionario, contador_pedido_vez, data"
    cur.execute(query, params)
    dados = cur.fetchall()

    if len(dados) == 0:
        st.write("Nenhum pedido encontrado com esses filtros")
        cur.close()
        conn.close()
        return

    # organizar pedidos por mesa + funcionário + contador_pedido_vez
    from collections import defaultdict
    mesas_dict = defaultdict(lambda: defaultdict(list))  # mesas_dict[mesa][funcionario] = list de sessões

    for mesa, data_hora, funcionario, produto, quantidade, valor_unitario, total, flag_cancel, flag_fim, contador in dados:
        # cada contador_pedido_vez representa uma sessão
        mesas_dict[mesa][funcionario].append({
            "contador": contador,
            "data": data_hora,
            "produto": produto,
            "quantidade": quantidade,
            "valor_unitario": valor_unitario,
            "subtotal": quantidade * valor_unitario,
            "cancelado": flag_cancel,
            "fim_atendimento": flag_fim
        })

    # exibir pedidos por sessão
    for mesa, funcionarios_sessoes in mesas_dict.items():
        for funcionario, pedidos in funcionarios_sessoes.items():
            # agrupar por contador_pedido_vez
            sessoes = defaultdict(list)
            for p in pedidos:
                sessoes[p["contador"]].append(p)

            for contador, sessao in sorted(sessoes.items()):
                # ordenar por data
                sessao.sort(key=lambda x: x["data"])
                inicio = sessao[0]["data"]
                fim = None
                for p in reversed(sessao):
                    if p["fim_atendimento"]:
                        fim = p["data"]
                        break

                inicio_str = inicio.strftime("%d/%m/%Y %H:%M")
                fim_str = fim.strftime("%d/%m/%Y %H:%M") if fim else "Em andamento"

                st.write(f"### Mesa {mesa} - {funcionario}")
                st.write(f"Início atendimento: {inicio_str} | Fim atendimento: {fim_str}")
                st.write("")  

                total_sessao = 0
                for p in sessao:
                    status = "" if fim else " (Ativo)"
                    st.write(f"{p['produto']} x {p['quantidade']} R${p['valor_unitario']:.2f} - Subtotal: {p['subtotal']:.2f}{status}")
                    total_sessao += p['subtotal']

                st.write(f"**Total da sessão: {total_sessao:.2f}**")
                st.markdown("---")  
                
    cur.close()
    conn.close()