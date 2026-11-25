"""Relatórios: Function que retorna tabela (parte 1) e telas do terminal (parte 2)."""
import clientes
from utils import ler_inteiro, pausar

# ======================================================================
# PARTE 1: COMANDOS SQL
# ======================================================================


def historico_cliente(conn, cliente_id):
    """FUNCTION que retorna TABELA: histórico de vendas de um cliente.

    Como retorna várias linhas e colunas, é chamada com SELECT ... FROM.
    """
    with conn.cursor() as cur:
        cur.execute(
            "SELECT venda_id, data_venda, total, status "
            "FROM fn_vendas_cliente(%s)",
            (cliente_id,),
        )
        return cur.fetchall()


def itens_da_venda(conn, venda_id):
    """READ com JOIN: itens de uma venda com o nome do produto."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT p.nome, i.quantidade, i.preco_unitario, "
            "       i.quantidade * i.preco_unitario AS subtotal "
            "FROM item_venda i "
            "JOIN produto p ON p.id = i.produto_id "
            "WHERE i.venda_id = %s "
            "ORDER BY i.id",
            (venda_id,),
        )
        return cur.fetchall()


def ultimos_logs(conn, limite=20):
    """READ com JOIN: registros gravados pelo TRIGGER na tabela log_estoque."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT l.id, p.nome, l.estoque_antigo, l.estoque_novo, "
            "       l.estoque_novo - l.estoque_antigo AS variacao, l.data_log "
            "FROM log_estoque l "
            "JOIN produto p ON p.id = l.produto_id "
            "ORDER BY l.id DESC LIMIT %s",
            (limite,),
        )
        return cur.fetchall()


# ======================================================================
# PARTE 2: TELAS DO TERMINAL
# ======================================================================


def tela_historico(conn):
    print("\n--- Histórico de compras do cliente ---\n")
    clientes.mostrar_tabela(clientes.listar(conn))
    cliente_id = ler_inteiro("\nId do cliente (0 para voltar): ", minimo=0)
    if cliente_id == 0:
        return
    cliente = clientes.buscar(conn, cliente_id)
    if cliente is None:
        print("\n=> Cliente não encontrado.")
        return

    vendas = historico_cliente(conn, cliente_id)
    if not vendas:
        print(f"\n=> [{cliente[1]}] ainda não têm vendas.")
        return

    print(f"\n=> Vendas de [{cliente[1]}]:\n")
    print(f"{'VENDA':<8}{'DATA':<20}{'TOTAL (R$)':>12}  {'STATUS':<12}")
    print("-" * 54)
    for venda_id, data, total, status in vendas:
        data_txt = data.strftime("%d/%m/%Y %H:%M:%S")
        print(f"{venda_id:<8}{data_txt:<20}{total:>12.2f}  {status:<12}")

    ids_validos = {v[0] for v in vendas}
    while True:
        venda_id = ler_inteiro("\nId da venda para ver os itens (0 para voltar): ", minimo=0)
        if venda_id == 0:
            return
        if venda_id not in ids_validos:
            print("\n=> Essa venda não pertence a este cliente.")
            continue
        itens = itens_da_venda(conn, venda_id)
        print(f"\n=> Itens da venda [{venda_id}]:\n")
        print(f"{'PRODUTO':<28}{'QTD':>5}{'UNIT. (R$)':>13}{'SUBTOTAL':>12}")
        print("-" * 58)
        for nome, qtd, unit, subtotal in itens:
            print(f"{nome:<28}{qtd:>5}{unit:>13.2f}{subtotal:>12.2f}")


def tela_log_estoque(conn):
    print("\n--- Log de estoque (gerado pelo Trigger) ---\n")
    logs = ultimos_logs(conn)
    if not logs:
        print("\n=> Nenhum registro no log ainda.")
        return
    print(f"{'ID':<6}{'PRODUTO':<26}{'ANTES':>7}{'DEPOIS':>8}{'VARIAÇÃO':>10}  {'DATA':<20}")
    print("-" * 79)
    for log_id, nome, antigo, novo, variacao, data in logs:
        print(
            f"{log_id:<6}{nome:<26}{antigo:>7}{novo:>8}{variacao:>+10}  "
            f"{data:%d/%m/%Y %H:%M:%S}"
        )


def menu_relatorios(conn):
    while True:
        print("\n===== RELATÓRIOS =====\n")
        print("[1] - Histórico de compras de um cliente")
        print("[2] - Log de estoque (Trigger)")
        print("[0] - Voltar")
        opcao = input("\nEscolha: ").strip()

        if opcao == "1":
            tela_historico(conn)
            pausar()
        elif opcao == "2":
            tela_log_estoque(conn)
            pausar()
        elif opcao == "0":
            return
        else:
            print("\n=> [OPÇÃO INVÁLIDA!]")
