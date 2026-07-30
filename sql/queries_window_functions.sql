-- Window functions sobre o star schema - Módulo 2

-- ============================================================
-- 1. RANK() - ranking de deputados por gasto total
-- ============================================================
SELECT
    d.nome,
    d.sigla_partido,
    d.sigla_uf,
    SUM(f.valor_documento) AS total_gasto,
    RANK() OVER (ORDER BY SUM(f.valor_documento) DESC) AS ranking
FROM fact_despesas f
JOIN dim_deputado d ON d.id = f.deputado_id
GROUP BY d.id, d.nome, d.sigla_partido, d.sigla_uf
ORDER BY ranking;

-- ============================================================
-- 2. AVG() OVER RANGE - média móvel de 3 meses por deputado
-- ============================================================
WITH gasto_mensal AS (
    SELECT
        f.deputado_id,
        make_date(t.ano, t.mes, 1) AS mes_ref,
        SUM(f.valor_documento) AS total_mes
    FROM fact_despesas f
    JOIN dim_tempo t ON t.id_tempo = f.id_tempo
    GROUP BY f.deputado_id, make_date(t.ano, t.mes, 1)
)
SELECT
    deputado_id,
    mes_ref,
    total_mes,
    AVG(total_mes) OVER (
        PARTITION BY deputado_id
        ORDER BY mes_ref
        RANGE BETWEEN INTERVAL '2 months' PRECEDING AND CURRENT ROW
    ) AS media_movel_3m
FROM gasto_mensal
ORDER BY deputado_id, mes_ref;

-- ============================================================
-- 3. LAG() - variação de gasto mês a mês por deputado
-- ============================================================
WITH gasto_mensal AS (
    SELECT
        f.deputado_id,
        make_date(t.ano, t.mes, 1) AS mes_ref,
        SUM(f.valor_documento) AS total_mes
    FROM fact_despesas f
    JOIN dim_tempo t ON t.id_tempo = f.id_tempo
    GROUP BY f.deputado_id, make_date(t.ano, t.mes, 1)
)
SELECT
    deputado_id,
    mes_ref,
    total_mes,
    total_mes - LAG(total_mes) OVER (
        PARTITION BY deputado_id ORDER BY mes_ref
    ) AS variacao_vs_mes_anterior
FROM gasto_mensal
ORDER BY deputado_id, mes_ref;
