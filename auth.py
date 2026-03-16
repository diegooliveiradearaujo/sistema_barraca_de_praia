from db import conectar

def autenticar(usuario, senha):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        """SELECT nome, tipo
        FROM funcionarios
        WHERE nome = %s
        AND senha = %s
        """,
        (usuario, senha)
    )
    resultado = cursor.fetchone()

    cursor.close()
    conn.close()

    return resultado