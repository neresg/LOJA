"""Modelo de configuração do banco.

Como usar:
  1. Copie este arquivo e renomeie a cópia para config_local.py
  2. Troque SUA_SENHA_AQUI pela senha do seu PostgreSQL

O config_local.py está no .gitignore e não vai para o repositório.
"""

DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "dbname": "loja_vendas",
    "user": "postgres",
    "password": "SUA_SENHA_AQUI",
}
