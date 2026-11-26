-- =====================================================
-- Sistema de Vendas com Controle de Estoque
-- Banco de Dados II - IFPI Campus Picos - 2026.2
-- PostgreSQL 11 ou superior
-- =====================================================

-- Para recriar tudo do zero (útil durante os testes)
DROP TABLE IF EXISTS log_estoque CASCADE;
DROP TABLE IF EXISTS item_venda  CASCADE;
DROP TABLE IF EXISTS venda       CASCADE;
DROP TABLE IF EXISTS produto     CASCADE;
DROP TABLE IF EXISTS cliente     CASCADE;

-- =====================================================
-- 1. TABELAS
-- =====================================================

CREATE TABLE cliente (
    id        SERIAL PRIMARY KEY,
    nome      VARCHAR(100) NOT NULL,
    cpf       VARCHAR(14)  NOT NULL UNIQUE,
    email     VARCHAR(100),
    telefone  VARCHAR(20)
);

CREATE TABLE produto (
    id        SERIAL PRIMARY KEY,
    nome      VARCHAR(100)  NOT NULL,
    preco     NUMERIC(10,2) NOT NULL CHECK (preco > 0),
    estoque   INTEGER       NOT NULL DEFAULT 0 CHECK (estoque >= 0)
);

CREATE TABLE venda (
    id          SERIAL PRIMARY KEY,
    cliente_id  INTEGER NOT NULL REFERENCES cliente(id),
    data_venda  TIMESTAMP NOT NULL DEFAULT NOW(),
    total       NUMERIC(10,2) NOT NULL DEFAULT 0,
    status      VARCHAR(20) NOT NULL DEFAULT 'ABERTA'
                CHECK (status IN ('ABERTA', 'CONCLUIDA', 'CANCELADA'))
);

CREATE TABLE item_venda (
    id              SERIAL PRIMARY KEY,
    venda_id        INTEGER NOT NULL REFERENCES venda(id) ON DELETE CASCADE,
    produto_id      INTEGER NOT NULL REFERENCES produto(id),
    quantidade      INTEGER NOT NULL CHECK (quantidade > 0),
    preco_unitario  NUMERIC(10,2) NOT NULL
);

CREATE TABLE log_estoque (
    id          SERIAL PRIMARY KEY,
    produto_id  INTEGER NOT NULL REFERENCES produto(id),
    estoque_antigo INTEGER,
    estoque_novo   INTEGER,
    data_log    TIMESTAMP NOT NULL DEFAULT NOW()
);

-- =====================================================
-- 2. DADOS DE TESTE
-- =====================================================

INSERT INTO cliente (nome, cpf, email, telefone) VALUES
('Maria Silva',  '111.111.111-11', 'maria@email.com', '(89) 99999-0001'),
('João Santos',  '222.222.222-22', 'joao@email.com',  '(89) 99999-0002'),
('Ana Oliveira', '333.333.333-33', 'ana@email.com',   '(89) 99999-0003');

INSERT INTO produto (nome, preco, estoque) VALUES
('Caderno 100 folhas', 12.50, 50),
('Caneta azul',         2.00, 200),
('Mochila escolar',    89.90, 10),
('Lápis HB',            1.50, 150);

-- =====================================================
-- 3. FUNCTIONS
-- =====================================================

-- 3.1 Function escalar: retorna o estoque atual de um produto
--     (retorna 0 se o produto não existir)
CREATE OR REPLACE FUNCTION fn_estoque_disponivel(p_produto_id INTEGER)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_estoque INTEGER;
BEGIN
    SELECT p.estoque INTO v_estoque
    FROM produto p
    WHERE p.id = p_produto_id;

    RETURN COALESCE(v_estoque, 0);
END;
$$;

-- 3.2 Function escalar: calcula o total de uma venda
--     somando quantidade * preço unitário dos itens
CREATE OR REPLACE FUNCTION fn_total_venda(p_venda_id INTEGER)
RETURNS NUMERIC
LANGUAGE plpgsql
AS $$
DECLARE
    v_total NUMERIC;
BEGIN
    SELECT COALESCE(SUM(i.quantidade * i.preco_unitario), 0)
    INTO v_total
    FROM item_venda i
    WHERE i.venda_id = p_venda_id;

    RETURN v_total;
END;
$$;

-- 3.3 Function que retorna TABELA: histórico de vendas de um cliente
CREATE OR REPLACE FUNCTION fn_vendas_cliente(p_cliente_id INTEGER)
RETURNS TABLE (
    venda_id   INTEGER,
    data_venda TIMESTAMP,
    total      NUMERIC,
    status     VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT v.id, v.data_venda, v.total, v.status
    FROM venda v
    WHERE v.cliente_id = p_cliente_id
    ORDER BY v.data_venda DESC;
END;
$$;

-- =====================================================
-- 4. PROCEDURE (com controle de transação)
-- =====================================================

-- Realiza uma venda completa:
--   1) valida os dados e o cliente
--   2) cria a venda
--   3) para cada item: valida produto e estoque (usando fn_estoque_disponivel),
--      insere o item e dá baixa no estoque
--   4) calcula o total (usando fn_total_venda) e conclui a venda

-- Se qualquer validação falhar -> ROLLBACK (desfaz TUDO)
-- Se tudo der certo            -> COMMIT

-- Parâmetros de entrada(p): cliente, lista de produtos e lista de quantidades
-- Parâmetros INOUT (saída): id da venda criada e mensagem do resultado

CREATE OR REPLACE PROCEDURE sp_realizar_venda(
    p_cliente_id  INTEGER,
    p_produtos    INTEGER[], 
    p_quantidades INTEGER[],
    INOUT p_venda_id  INTEGER DEFAULT NULL,
    INOUT p_mensagem  TEXT    DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_preco   NUMERIC;
    v_estoque INTEGER;
BEGIN
    -- Validação das listas
    IF p_produtos IS NULL OR p_quantidades IS NULL
       OR array_length(p_produtos, 1) IS NULL
       OR array_length(p_produtos, 1) <> array_length(p_quantidades, 1) THEN -- ex: 2 prod e 1 qtd
        p_mensagem := 'ERRO: lista de produtos/quantidades inválida.';
        ROLLBACK;
        RETURN;
    END IF;

    -- Validação do cliente
    IF NOT EXISTS (SELECT 1 FROM cliente WHERE id = p_cliente_id) THEN
        p_mensagem := 'ERRO: cliente ' || COALESCE(p_cliente_id::TEXT, 'nulo')
                      || ' não existe.';
        ROLLBACK;
        RETURN;
    END IF;

    -- Cria a venda (cabeçalho)
    INSERT INTO venda (cliente_id)
    VALUES (p_cliente_id)
    RETURNING id INTO p_venda_id;

    -- Processa cada item
    FOR i IN 1 .. array_length(p_produtos, 1) LOOP

        IF p_quantidades[i] IS NULL OR p_quantidades[i] <= 0 THEN
            p_mensagem := 'ERRO: quantidade inválida para o produto '
                          || p_produtos[i] || '. Venda cancelada.';
            p_venda_id := NULL;
            ROLLBACK;
            RETURN;
        END IF;

        SELECT preco INTO v_preco   -- busca o preço e guarda na variável
        FROM produto
        WHERE id = p_produtos[i];

        IF NOT FOUND THEN
            p_mensagem := 'ERRO: produto ' || p_produtos[i]
                          || ' não existe. Venda cancelada.';
            p_venda_id := NULL;
            ROLLBACK;
            RETURN;
        END IF;

        -- Usa a FUNCTION para consultar o estoque
        v_estoque := fn_estoque_disponivel(p_produtos[i]);

        IF v_estoque < p_quantidades[i] THEN
            p_mensagem := 'ERRO: estoque insuficiente para o produto '
                          || p_produtos[i] || ' (disponível: ' || v_estoque
                          || ', pedido: ' || p_quantidades[i]
                          || '). Venda cancelada.';
            p_venda_id := NULL;
            ROLLBACK;
            RETURN;
        END IF;

        INSERT INTO item_venda (venda_id, produto_id, quantidade, preco_unitario) -- grava na nota
        VALUES (p_venda_id, p_produtos[i], p_quantidades[i], v_preco);

        -- Baixa no estoque
        UPDATE produto          -- dispara o trigger de log_estoque
        SET estoque = estoque - p_quantidades[i]
        WHERE id = p_produtos[i];
    END LOOP;

    -- Usa a FUNCTION para calcular o total e conclui a venda
    UPDATE venda
    SET total  = fn_total_venda(p_venda_id),
        status = 'CONCLUIDA'
    WHERE id = p_venda_id;

    p_mensagem := 'Venda ' || p_venda_id || ' concluída com sucesso.';
    COMMIT;
END;
$$;

-- =====================================================
-- 5. TRIGGER
-- =====================================================
-- Sempre que o estoque de um produto mudar (por venda, reposição
-- ou ajuste manual), registra o valor antigo e o novo em log_estoque.
-- A baixa do estoque continua sendo feita pela PROCEDURE; o trigger
-- só faz a auditoria (sem duplicar a baixa).

-- 5.1 Function do trigger (deve retornar TRIGGER)
CREATE OR REPLACE FUNCTION trg_fn_log_estoque()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.estoque IS DISTINCT FROM OLD.estoque THEN
        INSERT INTO log_estoque (produto_id, estoque_antigo, estoque_novo)
        VALUES (OLD.id, OLD.estoque, NEW.estoque);
    END IF;

    RETURN NEW;
END;
$$;

-- 5.2 Trigger: dispara DEPOIS de um UPDATE na coluna estoque, para cada linha
DROP TRIGGER IF EXISTS trg_produto_log_estoque ON produto;

CREATE TRIGGER trg_produto_log_estoque
AFTER UPDATE OF estoque ON produto
FOR EACH ROW
EXECUTE FUNCTION trg_fn_log_estoque();
