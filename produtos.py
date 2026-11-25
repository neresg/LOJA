"""CRUD de produtos: comandos SQL (parte 1) e menu do terminal (parte 2)."""
from psycopg2 import errors

from utils import ler_decimal, ler_inteiro, ler_texto, pausar

# ======================================================================
# PARTE 1: COMANDOS SQL (CRUD)
# ======================================================================


def listar(conn):
    """READ: retorna todos os produtos."""
    with conn.cursor() as cur:
        cur.execute("SELECT id, nome, preco, estoque FROM produto ORDER BY id")
        return cur.fetchall()


def buscar(conn, produto_id):
    """READ: retorna um produto pelo id (ou None)."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, nome, preco, estoque FROM produto WHERE id = %s",
            (produto_id,),
        )
        return cur.fetchone()


def inserir(conn, nome, preco, estoque):
    """CREATE: insere um produto e retorna o id gerado."""
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO produto (nome, preco, estoque) "
            "VALUES (%s, %s, %s) RETURNING id",
            (nome, preco, estoque),
        )
        return cur.fetchone()[0]


def atualizar(conn, produto_id, nome, preco, estoque):
    """UPDATE: altera um produto. Retorna quantas linhas foram alteradas."""
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE produto SET nome = %s, preco = %s, estoque = %s WHERE id = %s",
            (nome, preco, estoque, produto_id),
        )
        return cur.rowcount


def excluir(conn, produto_id):
    """DELETE: remove um produto. Retorna quantas linhas foram removidas."""
    with conn.cursor() as cur:
        cur.execute("DELETE FROM produto WHERE id = %s", (produto_id,))
        return cur.rowcount


# ======================================================================
# PARTE 2: MENU DO TERMINAL
# ======================================================================


def mostrar_tabela(produtos):
    if not produtos:
        print("Nenhum produto cadastrado.")
        return
    print(f"\n{'ID':<5}{'NOME':<30}{'PREÇO (R$)':>12}{'ESTOQUE':>10}")
    print("-" * 57)
    for pid, nome, preco, estoque in produtos:
        print(f"{pid:<5}{nome:<30}{preco:>12.2f}{estoque:>10}")


def tela_cadastrar(conn):
    print("\n--- Cadastrar produto ---\n")
    nome = ler_texto("Nome: ")
    preco = ler_decimal("Preço: ")
    estoque = ler_inteiro("Estoque inicial: ", minimo=0)
    try:
        novo_id = inserir(conn, nome, preco, estoque)
        print(f"\n-> Produto cadastrado com o id {novo_id}.")
    except errors.CheckViolation:
        print("Erro: o banco recusou os dados (preço deve ser > 0 e estoque >= 0).")


def tela_atualizar(conn):
    print("\n--- Atualizar produto ---\n")
    produto_id = ler_inteiro("Id do produto: ", minimo=1)
    produto = buscar(conn, produto_id)
    if produto is None:
        print("\n=> Produto não encontrado.")
        return

    print("\n(Pressione Enter para manter o valor atual)\n")
    nome = ler_texto(f"Nome [{produto[1]}]: ", padrao=produto[1])
    preco = ler_decimal(f"Preço [{produto[2]}]: ", padrao=produto[2])
    estoque = ler_inteiro(f"Estoque [{produto[3]}]: ", minimo=0, padrao=produto[3])
    try:
        atualizar(conn, produto_id, nome, preco, estoque)
        print("\n=> Produto atualizado.")
    except errors.CheckViolation:
        print("Erro: o banco recusou os dados (preço deve ser > 0 e estoque >= 0).")


def tela_excluir(conn):
    print("\n--- Excluir produto ---\n")
    produto_id = ler_inteiro("Id do produto: ", minimo=1)
    produto = buscar(conn, produto_id)
    if produto is None:
        print("\n=> Produto não encontrado.")
        return

    confirma = input(f"Excluir '{produto[1]}'? (s/n): ").strip().lower()
    if confirma != "s":
        print("\n=> Operação cancelada!")
        return
    try:
        excluir(conn, produto_id)
        print("\n=> Produto excluído.")
    except errors.ForeignKeyViolation:
        print(
            "Não é possível excluir: este produto já possui vendas "
            "ou histórico de estoque."
        )


def menu_produtos(conn):
    while True:
        print("\n===== PRODUTOS =====\n")
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
