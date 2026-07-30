-- Star schema do Projeto Lupa - Módulo 2
-- Construído a partir das tabelas raw_deputados / raw_despesas (dado bruto da API)

-- ============================================================
-- DIMENSÕES
-- ============================================================

CREATE TABLE IF NOT EXISTS dim_deputado (
    id INTEGER PRIMARY KEY,           -- mesmo id da API, já é único
    nome TEXT NOT NULL,
    sigla_partido TEXT,
    sigla_uf TEXT,
    id_legislatura INTEGER
);

CREATE TABLE IF NOT EXISTS dim_fornecedor (
    id_fornecedor SERIAL PRIMARY KEY,  -- chave criada por nós (não existe na API)
    nome_fornecedor TEXT NOT NULL,
    cnpj_cpf_fornecedor TEXT,
    UNIQUE (cnpj_cpf_fornecedor, nome_fornecedor)
);

CREATE TABLE IF NOT EXISTS dim_categoria_despesa (
    id_categoria SERIAL PRIMARY KEY,   -- chave criada por nós
    tipo_despesa TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS dim_tempo (
    id_tempo SERIAL PRIMARY KEY,       -- chave criada por nós
    ano INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    trimestre INTEGER NOT NULL,
    UNIQUE (ano, mes)
);

-- ============================================================
-- FATO
-- ============================================================

CREATE TABLE IF NOT EXISTS fact_despesas (
    id_despesa SERIAL PRIMARY KEY,
    deputado_id INTEGER NOT NULL REFERENCES dim_deputado (id),
    id_fornecedor INTEGER REFERENCES dim_fornecedor (id_fornecedor),
    id_categoria INTEGER REFERENCES dim_categoria_despesa (id_categoria),
    id_tempo INTEGER NOT NULL REFERENCES dim_tempo (id_tempo),
    cod_documento TEXT,
    num_documento TEXT,
    valor_documento NUMERIC,
    valor_liquido NUMERIC,
    valor_glosa NUMERIC,
    UNIQUE (deputado_id, cod_documento, num_documento)
);
