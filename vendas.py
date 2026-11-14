"""Vendas: chamadas à Function e à Procedure (parte 1) e tela do terminal (parte 2)."""
from decimal import Decimal

import clientes
import produtos
from utils import ler_inteiro, pausar

# ======================================================================
# PARTE 1: COMANDOS SQL (FUNCTIONS e PROCEDURE)
# ======================================================================


def estoque_disponivel(conn, produto_id):
    """FUNCTION escalar: consulta o estoque atual do produto."""
    with conn.cursor() as cur:
        cur.execute("SELECT fn_estoque_disponivel(%s)", (produto_id,))
        return cur.fetchone()[0]


def total_venda(conn, venda_id):
    """FUNCTION escalar: total calculado pelo banco para a venda."""
    with conn.cursor() as cur:
        cur.execute("SELECT fn_total_venda(%s)", (venda_id,))
        return cur.fetchone()[0]


def realizar_venda(conn, cliente_id, ids_produtos, quantidades):
    """PROCEDURE: executa a venda inteira dentro do banco.

    A procedure controla a transação: se algo falhar, faz ROLLBACK e devolve
    p_venda_id = NULL com uma mensagem de erro; se der certo, faz COMMIT.
    Retorna (venda_id, mensagem), os dois parâmetros INOUT da procedure.
    """
    with conn.cursor() as cur:
        cur.execute(
            "CALL sp_realizar_venda(%s, %s::integer[], %s::integer[], NULL, NULL)",
            (cliente_id, ids_produtos, quantidades),
        )
        venda_id, mensagem = cur.fetchone()
        return venda_id, mensagem


# ======================================================================
# PARTE 2: TELA DO TERMINAL
# ======================================================================


def mostrar_carrinho(carrinho):
    print(f"\n{'ID':<5}{'PRODUTO':<28}{'QTD':>5}{'UNIT. (R$)':>13}{'SUBTOTAL':>12}")
    print("-" * 63)
    soma = Decimal("0")
    for pid, item in carrinho.items():
        subtotal = item["preco"] * item["qtd"]
        soma += subtotal
        print(
            f"{pid:<5}{item['nome']:<28}{item['qtd']:>5}"
            f"{item['preco']:>13.2f}{subtotal:>12.2f}"
        )
    print("-" * 63)
    print(f"{'Prévia do total:':<51}{soma:>12.2f}")


def tela_nova_venda(conn):
    print("\n===== NOVA VENDA =====")

    # 1) Escolher o cliente
    clientes.mostrar_tabela(clientes.listar(conn))
    cliente_id = ler_inteiro("\nId do cliente (0 para cancelar): ", minimo=0)
    if cliente_id == 0:
        print("Venda cancelada.")
        return
    cliente = clientes.buscar(conn, cliente_id)
    if cliente is None:
        print("Cliente não encontrado.")
        return
    print(f"Cliente: {cliente[1]}")

    # 2) Montar o carrinho
    carrinho = {}  # produto_id -> {"nome", "preco", "qtd"}
    produtos.mostrar_tabela(produtos.listar(conn))

    while True:
        print("\nAdicionar item (digite 0 no id do produto para finalizar)")
        produto_id = ler_inteiro("Id do produto: ", minimo=0)
        if produto_id == 0:
            break

        produto = produtos.buscar(conn, produto_id)
        if produto is None:
            print("Produto não encontrado.")
            continue

        quantidade = ler_inteiro("Quantidade: ", minimo=1)
        ja_no_carrinho = carrinho[produto_id]["qtd"] if produto_id in carrinho else 0
        total_pedido = ja_no_carrinho + quantidade

        # Aviso usando a FUNCTION. A decisão final continua sendo da procedure.
        disponivel = estoque_disponivel(conn, produto_id)
        if total_pedido > disponivel:
            print(
                f"Atenção: estoque disponível de '{produto[1]}' é {disponivel} "
                f"(pedido: {total_pedido}). A venda poderá ser recusada."
            )

        carrinho[produto_id] = {
            "nome": produto[1],
            "preco": produto[2],
            "qtd": total_pedido,
        }
        mostrar_carrinho(carrinho)

    if not carrinho:
        print("Carrinho vazio. Venda cancelada.")
        return

    # 3) Confirmar e chamar a PROCEDURE
    confirma = input("\nConfirmar a venda? (s/n): ").strip().lower()
    if confirma != "s":
        print("Venda cancelada.")
        return

    ids = list(carrinho.keys())
    quantidades = [carrinho[i]["qtd"] for i in ids]
    venda_id, mensagem = realizar_venda(conn, cliente_id, ids, quantidades)

    # 4) Mostrar o resultado
    print()
    if venda_id is not None:
        print(f"[OK] {mensagem}")
        print(f"Total registrado pelo banco: R$ {total_venda(conn, venda_id):.2f}")
    else:
        print(f"[FALHOU] {mensagem}")
        print("Nenhuma alteração foi mantida no banco (ROLLBACK).")


def menu_vendas(conn):
    tela_nova_venda(conn)
    pausar()
