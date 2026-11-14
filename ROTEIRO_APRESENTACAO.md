# Roteiro da apresentação (15 min)

**Sistema de Vendas com Controle de Estoque**: PostgreSQL + Python
Banco de Dados II, IFPI Campus Picos

| # | Etapa | Tempo |
|---|---|---|
| 1 | Introdução e problema | 1:00 |
| 2 | Requisitos e casos de uso | 0:45 |
| 3 | Diagrama do banco (DER) | 1:30 |
| 4 | Recursos SQL no banco | 1:30 |
| 5 | Demonstração do app | 6:00 |
| 6 | SQL no código da aplicação | 3:00 |
| 7 | Conclusão | 0:45 |
| | **Total** | **14:30** |

---

## Antes de entrar na sala

- [ ] PostgreSQL rodando
- [ ] **Banco zerado:** rodar o `script.sql` inteiro no DBeaver (Alt+X) para os dados voltarem ao início
- [ ] Testar a conexão do app uma vez (`python3 main.py`) e fechar
- [ ] Terminal com **fonte grande** e janela bem aberta
- [ ] Abertos e prontos: README (GitHub ou VS Code), `docs/casos_de_uso.png`, `docs/DER.png`, DBeaver com o `script.sql`, VS Code com `vendas.py`, `produtos.py` e `relatorios.py`
- [ ] No DBeaver, um editor SQL com estas consultas já digitadas:
  ```sql
  SELECT id, nome, estoque FROM produto ORDER BY id;
  SELECT * FROM venda;
  SELECT * FROM item_venda;
  SELECT * FROM log_estoque ORDER BY id;
  ```
- [ ] Plano B: prints da pasta `testes/` à mão, caso algo falhe
- [ ] Nenhuma tela mostrando a senha (`config_local.py` fechado)

---

## 1. Introdução e problema (1:00)

**Abrir:** README.

**Falar:**
- É um sistema de vendas com controle de estoque, feito em Python com PostgreSQL.
- O problema: numa venda, vários passos precisam acontecer juntos (criar a venda, registrar os itens, baixar o estoque). Se um falhar no meio, o banco não pode ficar com a venda pela metade.
- A solução é fazer a venda dentro de uma **transação**, controlada por uma **Procedure**: ou tudo é confirmado (COMMIT), ou tudo é desfeito (ROLLBACK).

---

## 2. Requisitos e casos de uso (0:45)

**Abrir:** `docs/casos_de_uso.png`.

**Falar:**
- O vendedor gerencia produtos e clientes, realiza vendas, consulta o histórico de compras e consulta o log de estoque.
- Realizar venda sempre inclui validar o estoque.

---

## 3. Diagrama do banco (1:30)

**Abrir:** `docs/DER.png`.

**Falar:**
- São 5 tabelas: `cliente`, `produto`, `venda`, `item_venda` e `log_estoque`.
- Um cliente tem várias vendas. Uma venda tem vários itens. Cada item aponta para um produto.
- `log_estoque` guarda o histórico de mudanças de estoque, e quem grava nela é o Trigger.
- O banco se protege sozinho: `CHECK` (preço > 0, estoque >= 0), `UNIQUE` (CPF) e chaves estrangeiras.

---

## 4. Recursos SQL no banco (1:30)

**Abrir:** DBeaver, `script.sql`. Rolar rapidamente pelas seções.

| Recurso | Onde no script | O que fazer |
|---|---|---|
| Functions | Seção 3 | Mostrar as 3: `fn_estoque_disponivel` e `fn_total_venda` (escalares) e `fn_vendas_cliente` (retorna tabela) |
| Procedure | Seção 4 | Mostrar o `ROLLBACK` nas validações e o `COMMIT` no final |
| Trigger | Seção 5 | Mostrar `AFTER UPDATE OF estoque` e o `IF NEW.estoque IS DISTINCT FROM OLD.estoque` |

**Falar:**
- A Procedure usa as Functions dentro dela, para checar o estoque e calcular o total.
- A baixa do estoque é da Procedure. O Trigger só registra o log, sem duplicar a baixa.

---

## 5. Demonstração do app (6:00)

**Abrir:** terminal, `python3 main.py`. Dados no estado inicial.

### 5.1 CRUD (1:00)
`1` Produtos > `2` Cadastrar: `Borracha`, preço `1,50`, estoque `30`. Depois `1` Listar.

> Mostra Create e Read. Atualizar e excluir funcionam da mesma forma, nos produtos e nos clientes.

Voltar ao menu principal (`0`).

### 5.2 Venda com sucesso, COMMIT (1:30)
`3` Nova venda:

| Pergunta | Digitar |
|---|---|
| Cliente | `2` (João) |
| Produto / quantidade | `1` / `2` |
| Produto / quantidade | `4` / `10` |
| Finalizar | `0` |
| Confirmar | `s` |

Resultado: `[OK] Venda 1 concluída`, total **40.00**.

**No DBeaver:** rodar as consultas de `produto`, `venda` e `item_venda`. Caderno **48** e Lápis **140**.

> Uma única chamada do app, um `CALL`, e a Procedure fez tudo.

### 5.3 Trigger (0:45)
`4` Relatórios > `2` Log de estoque. Aparecem as 2 baixas (`-2` e `-10`).

> O app não inseriu nada no log. Quem gravou foi o Trigger.

### 5.4 Venda com ROLLBACK (1:30)
`3` Nova venda:

| Pergunta | Digitar |
|---|---|
| Cliente | `1` (Maria) |
| Produto / quantidade | `4` / `5` |
| Produto / quantidade | `3` / `999` |
| Finalizar | `0` |
| Confirmar | `s` |

O app avisa sobre o estoque ao adicionar a Mochila (isso é a Function). Ao confirmar: `[FALHOU] ... estoque insuficiente`.

**No DBeaver:** rodar de novo `produto` e `log_estoque`. O Lápis continua **140** e o log continua com **2** linhas.

> O Lápis já tinha sido baixado quando o segundo item falhou. O ROLLBACK desfez tudo, inclusive o log do Trigger.

### 5.5 Histórico (1:00)
`4` Relatórios > `1` Histórico > cliente `2`. Aparece a venda 1. Digitar `1` para ver os itens.

> Essa tela chama a Function que retorna tabela, `fn_vendas_cliente`.

---

## 6. SQL no código da aplicação (3:00)

**Abrir:** VS Code.

| Arquivo | O que mostrar |
|---|---|
| `produtos.py` (e `clientes.py`) | `inserir`, `listar`, `atualizar`, `excluir`: o CRUD com `INSERT`, `SELECT`, `UPDATE` e `DELETE` |
| `vendas.py` | `realizar_venda()` com o `CALL sp_realizar_venda(...)`; `estoque_disponivel()` e `total_venda()` com `SELECT fn_...` |
| `relatorios.py` | `historico_cliente()` com `SELECT ... FROM fn_vendas_cliente(%s)` |
| `db.py` | `autocommit = True` |

**Falar:**
- O `autocommit` está ligado porque a Procedure faz COMMIT e ROLLBACK por conta própria. Se o Python abrisse uma transação antes, o PostgreSQL daria erro.
- Function escalar se chama com `SELECT fn(...)`. Function de tabela, com `SELECT * FROM fn(...)`. Procedure, com `CALL`.

---

## 7. Conclusão (0:45)

**Falar:**
- Cobrimos CRUD, Procedure com transação, Functions que ajudam a Procedure e Trigger de auditoria.
- A regra de negócio ficou no banco, então continua valendo mesmo que outro programa acesse os dados.
- Possíveis melhorias: cancelar venda, relatórios por período e interface gráfica.
- Tudo está no repositório, com os testes em `testes/`.

---

## Se perguntarem

- **Function x Procedure?** A Function retorna valor e é usada em consultas. A Procedure é chamada com `CALL` e pode controlar transação.
- **Por que o ROLLBACK desfez o log?** O Trigger roda dentro da mesma transação do `UPDATE`. Desfeita a transação, tudo é desfeito junto.
- **O que são OLD e NEW?** `OLD` é a linha antes da alteração, `NEW` é depois.
- **Por que o id da venda pula?** As sequências do PostgreSQL não voltam atrás depois de um ROLLBACK. A próxima venda aqui sai com id 3.
- **Por que `AFTER UPDATE OF estoque`?** Para registrar só depois de a alteração ser aceita e só quando o estoque mudar. Mudar o preço não gera log.

## Depois da apresentação

Rodar o `script.sql` de novo para deixar o banco limpo.
