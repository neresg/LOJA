# Testes realizados

Evidências (prints) dos testes do sistema, organizadas por pasta, na ordem em que foram executados.

**Como foi feito:** o banco `loja_vendas` foi zerado (`DROP SCHEMA public CASCADE; CREATE SCHEMA public;`)
e o `script.sql` foi executado do zero. Em seguida, os testes foram feitos pelo aplicativo
(`python3 main.py`) e, quando indicado, diretamente no DBeaver. Cada teste parte do estado deixado
pelo anterior.

| Pasta | O que comprova | Resultado esperado |
|---|---|---|
| `01_script_do_zero` | O `script.sql` roda em um banco vazio e cria todos os objetos | 5 tabelas, 4 functions (3 de negócio e 1 de trigger), 1 procedure e 1 trigger; 3 clientes e 4 produtos iniciais; functions respondendo corretamente |
| `02_crud_produtos` | CRUD de produtos pelo app | Listar, cadastrar, atualizar e excluir funcionam |
| `03_crud_clientes` | CRUD de clientes pelo app | Listar, cadastrar (CPF formatado), atualizar e excluir funcionam |
| `04_venda_sucesso` | **Procedure** com COMMIT | Venda e itens gravados, estoque baixado, total calculado pela function e status `CONCLUIDA` |
| `05_trigger_log` | **Trigger** de auditoria | `log_estoque` preenchido automaticamente em vendas e em reposições manuais; alterar só o preço não gera log |
| `06_venda_rollback` | **Procedure** com ROLLBACK | Venda recusada por estoque insuficiente; nenhuma venda, item, baixa de estoque ou log ficou no banco |
| `07_relatorios` | **Function que retorna tabela** (`fn_vendas_cliente`) e consulta ao log | Histórico por cliente, itens da venda e log de estoque completo |
| `08_integridade` | Erros tratados pelo banco e pelo app | CPF duplicado, exclusão com vendas, valores inválidos e validações da procedure com mensagens claras |

## Recursos SQL cobertos

- **CRUD:** pastas 02 e 03
- **Procedure (COMMIT e ROLLBACK):** pastas 04 e 06
- **Function (escalar e de tabela):** pastas 01, 04, 06 e 07
- **Trigger:** pasta 05
- **Integridade referencial e restrições (`FOREIGN KEY`, `UNIQUE`, `CHECK`):** pasta 08
