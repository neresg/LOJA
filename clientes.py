"""CRUD de clientes: comandos SQL (parte 1) e menu do terminal (parte 2)."""
from psycopg2 import errors

from utils import ler_cpf, ler_inteiro, ler_texto, pausar

# ======================================================================
# PARTE 1: COMANDOS SQL (CRUD)
# ======================================================================


def listar(conn):
    """READ: retorna todos os clientes."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, nome, cpf, email, telefone FROM cliente ORDER BY id"
        )
        return cur.fetchall()


def buscar(conn, cliente_id):
    """READ: retorna um cliente pelo id (ou None)."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, nome, cpf, email, telefone FROM cliente WHERE id = %s",
            (cliente_id,),
        )
        return cur.fetchone()


def inserir(conn, nome, cpf, email, telefone):
    """CREATE: insere um cliente e retorna o id gerado."""
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO cliente (nome, cpf, email, telefone) "
            "VALUES (%s, %s, %s, %s) RETURNING id",
            (nome, cpf, email, telefone),
        )
        return cur.fetchone()[0]


def atualizar(conn, cliente_id, nome, cpf, email, telefone):
    """UPDATE: altera um cliente. Retorna quantas linhas foram alteradas."""
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE cliente SET nome = %s, cpf = %s, email = %s, telefone = %s "
            "WHERE id = %s",
            (nome, cpf, email, telefone, cliente_id),
        )
        return cur.rowcount


def excluir(conn, cliente_id):
    """DELETE: remove um cliente. Retorna quantas linhas foram removidas."""
    with conn.cursor() as cur:
        cur.execute("DELETE FROM cliente WHERE id = %s", (cliente_id,))
        return cur.rowcount


# ======================================================================
# PARTE 2: MENU DO TERMINAL
# ======================================================================


def mostrar_tabela(clientes):
    if not clientes:
        print("\n=> Nenhum cliente cadastrado.")
        return
    print(f"\n{'ID':<5}{'NOME':<25}{'CPF':<16}{'EMAIL':<28}{'TELEFONE':<16}")
    print("-" * 90)
    for cid, nome, cpf, email, telefone in clientes:
        print(f"{cid:<5}{nome:<25}{cpf:<16}{email or '-':<28}{telefone or '-':<16}")


def tela_cadastrar(conn):
    print("\n--- Cadastrar cliente ---\n")
    nome = ler_texto("Nome: ")
    cpf = ler_cpf("CPF: ")
    email = ler_texto("Email (opcional): ", padrao="")
    telefone = ler_texto("Telefone (opcional): ", padrao="")
    try:
        novo_id = inserir(conn, nome, cpf, email or None, telefone or None)
        print(f"\n=> Cliente cadastrado com o id {novo_id}.")
    except errors.UniqueViolation:
        print("\n=> Erro: já existe um cliente cadastrado com esse CPF.")


def tela_atualizar(conn):
    print("\n--- Atualizar cliente ---\n")
    cliente_id = ler_inteiro("Id do cliente: ", minimo=1)
    cliente = buscar(conn, cliente_id)
    if cliente is None:
        print("\n=> Cliente não encontrado.")
        return

    print("\n(Pressione Enter para manter o valor atual)\n")
    nome = ler_texto(f"Nome [{cliente[1]}]: ", padrao=cliente[1])
    cpf = ler_cpf(f"CPF [{cliente[2]}]: ", padrao=cliente[2])
    email = ler_texto(f"Email [{cliente[3] or '-'}]: ", padrao=cliente[3] or "")
    telefone = ler_texto(f"Telefone [{cliente[4] or '-'}]: ", padrao=cliente[4] or "")
    try:
        atualizar(conn, cliente_id, nome, cpf, email or None, telefone or None)
        print("\n=> Cliente atualizado.")
    except errors.UniqueViolation:
        print("\n=> Erro: já existe outro cliente com esse CPF.")


def tela_excluir(conn):
    print("\n--- Excluir cliente ---\n")
    cliente_id = ler_inteiro("Id do cliente: ", minimo=1)
    cliente = buscar(conn, cliente_id)
    if cliente is None:
        print("\n=> Cliente não encontrado.")
        return

    confirma = input(f"Excluir '{cliente[1]}'? (s/n): ").strip().lower()
    if confirma != "s":
        print("\n=> Operação cancelada.")
        return
    try:
        excluir(conn, cliente_id)
        print("\n=> Cliente excluído.")
    except errors.ForeignKeyViolation:
        print("\n=> Não é possível excluir: este cliente já possui vendas registradas.")


def menu_clientes(conn):
    while True:
        print("\n===== CLIENTES =====\n")
        print("[1] - Listar")
        print("[2] - Cadastrar")
        print("[3] - Atualizar")
        print("[4] - Excluir")
        print("[0] - Voltar")
        opcao = input("\nEscolha: ").strip()

        if opcao == "1":
            mostrar_tabela(listar(conn))
            pausar()
        elif opcao == "2":
            tela_cadastrar(conn)
            pausar()
        elif opcao == "3":
            tela_atualizar(conn)
            pausar()
        elif opcao == "4":
            tela_excluir(conn)
            pausar()
        elif opcao == "0":
            return
        else:
            print("\n=> [OPÇÃO INVÁLIDA!]")
