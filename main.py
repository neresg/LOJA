"""Sistema de Vendas com Controle de Estoque (menu principal)."""
import psycopg2

import clientes
import produtos
import relatorios
import vendas
from db import conectar


def main():
    try:
        conn = conectar()
    except psycopg2.OperationalError as erro:
        print("Não foi possível conectar ao banco de dados:")
        print(erro)
        print("\nConfira o usuário/senha em db.py e se o PostgreSQL está rodando.")
        return

    print("Conectado ao banco com sucesso!")
    try:
        while True:
            print("\n===== SISTEMA DE VENDAS =====")
            print("1 - Produtos")
            print("2 - Clientes")
            print("3 - Nova venda")
            print("4 - Relatórios")
            print("0 - Sair")
            opcao = input("Escolha: ").strip()

            if opcao == "1":
                produtos.menu_produtos(conn)
            elif opcao == "2":
                clientes.menu_clientes(conn)
            elif opcao == "3":
                vendas.menu_vendas(conn)
            elif opcao == "4":
                relatorios.menu_relatorios(conn)
            elif opcao == "0":
                print("Até logo!")
                break
            else:
                print("Opção inválida.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
