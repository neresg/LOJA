"""Conexão com o banco PostgreSQL."""
import os

import psycopg2

# Ordem de busca da configuração:
#   1) config_local.py (arquivo local com a sua senha, fora do repositório)
#   2) variáveis de ambiente DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
try:
    from config_local import DB_CONFIG
except ImportError:
    DB_CONFIG = {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "5432"),
        "dbname": os.getenv("DB_NAME", "loja_vendas"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", ""),
    }


def conectar():
    """Abre a conexão com o banco.

    autocommit=True é necessário porque a Procedure sp_realizar_venda
    controla a transação sozinha (COMMIT/ROLLBACK dentro dela). Se o Python
    abrisse uma transação antes do CALL, o PostgreSQL daria erro.
    """
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    return conn
