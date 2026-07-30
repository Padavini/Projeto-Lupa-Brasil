-- Views de KPI do Projeto Lupa - Módulo 2
-- Todas construídas sobre o star schema (fact_despesas + dim_*)

-- Gasto total e quantidade de despesas por deputado
CREATE OR REPLACE VIEW vw_gasto_por_deputado AS
SELECT
    d.id AS deputado_id,
    d.nome,
    d.sigla_partido,
    d.sigla_uf,
    SUM(f.valor_documento) AS total_gasto,
    COUNT(*) AS qtd_despesas
FROM fact_despesas f
JOIN dim_deputado d ON d.id = f.deputado_id
GROUP BY d.id, d.nome, d.sigla_partido, d.sigla_uf;

-- Gasto total por partido
CREATE OR REPLACE VIEW vw_gasto_por_partido AS
SELECT
    d.sigla_partido,
    SUM(f.valor_documento) AS total_gasto,
    COUNT(DISTINCT d.id) AS qtd_deputados,
    SUM(f.valor_documento) / COUNT(DISTINCT d.id) AS gasto_medio_por_deputado
FROM fact_despesas f
JOIN dim_deputado d ON d.id = f.deputado_id
GROUP BY d.sigla_partido
ORDER BY total_gasto DESC;

-- Gasto total por UF
CREATE OR REPLACE VIEW vw_gasto_por_uf AS
SELECT
    d.sigla_uf,
    SUM(f.valor_documento) AS total_gasto,
    COUNT(DISTINCT d.id) AS qtd_deputados,
    SUM(f.valor_documento) / COUNT(DISTINCT d.id) AS gasto_medio_por_deputado
FROM fact_despesas f
JOIN dim_deputado d ON d.id = f.deputado_id
GROUP BY d.sigla_uf
ORDER BY total_gasto DESC;

-- Ticket médio por categoria de despesa
CREATE OR REPLACE VIEW vw_ticket_medio_categoria AS
SELECT
    c.tipo_despesa,
    AVG(f.valor_documento) AS ticket_medio,
    COUNT(*) AS qtd_despesas,
    SUM(f.valor_documento) AS total_gasto
FROM fact_despesas f
JOIN dim_categoria_despesa c ON c.id_categoria = f.id_categoria
GROUP BY c.tipo_despesa
ORDER BY ticket_medio DESC;

-- Top 10 fornecedores que mais receberam
CREATE OR REPLACE VIEW vw_top10_fornecedores AS
SELECT
    fo.nome_fornecedor,
    fo.cnpj_cpf_fornecedor,
    SUM(f.valor_documento) AS total_recebido,
    COUNT(*) AS qtd_despesas
FROM fact_despesas f
JOIN dim_fornecedor fo ON fo.id_fornecedor = f.id_fornecedor
GROUP BY fo.nome_fornecedor, fo.cnpj_cpf_fornecedor
ORDER BY total_recebido DESC
LIMIT 10;
