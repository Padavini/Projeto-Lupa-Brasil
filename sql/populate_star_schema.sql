-- Popula o star schema a partir das tabelas raw_* (dado bruto da API)
-- Ordem importa: dimensões primeiro (fact_despesas depende delas via FK)

-- 1. dim_deputado - direto de raw_deputados, mesmo id
INSERT INTO dim_deputado (id, nome, sigla_partido, sigla_uf, id_legislatura)
SELECT id, nome, sigla_partido, sigla_uf, id_legislatura
FROM raw_deputados
ON CONFLICT (id) DO UPDATE SET
    nome = EXCLUDED.nome,
    sigla_partido = EXCLUDED.sigla_partido,
    sigla_uf = EXCLUDED.sigla_uf,
    id_legislatura = EXCLUDED.id_legislatura;

-- 2. dim_fornecedor - valores distintos, sem repetir o mesmo fornecedor
INSERT INTO dim_fornecedor (nome_fornecedor, cnpj_cpf_fornecedor)
SELECT DISTINCT nome_fornecedor, cnpj_cpf_fornecedor
FROM raw_despesas
WHERE nome_fornecedor IS NOT NULL
ON CONFLICT (cnpj_cpf_fornecedor, nome_fornecedor) DO NOTHING;

-- 3. dim_categoria_despesa - tipos distintos de despesa
INSERT INTO dim_categoria_despesa (tipo_despesa)
SELECT DISTINCT tipo_despesa
FROM raw_despesas
WHERE tipo_despesa IS NOT NULL
ON CONFLICT (tipo_despesa) DO NOTHING;

-- 4. dim_tempo - combinações distintas de ano/mês, com trimestre calculado
INSERT INTO dim_tempo (ano, mes, trimestre)
SELECT DISTINCT ano, mes, CEIL(mes::numeric / 3)::int AS trimestre
FROM raw_despesas
WHERE ano IS NOT NULL AND mes IS NOT NULL
ON CONFLICT (ano, mes) DO NOTHING;

-- 5. fact_despesas - une cada despesa bruta às chaves substitutas das dimensões
INSERT INTO fact_despesas (
    deputado_id, id_fornecedor, id_categoria, id_tempo,
    cod_documento, num_documento, valor_documento, valor_liquido, valor_glosa
)
SELECT
    r.deputado_id,
    f.id_fornecedor,
    c.id_categoria,
    t.id_tempo,
    r.cod_documento,
    r.num_documento,
    r.valor_documento,
    r.valor_liquido,
    r.valor_glosa
FROM raw_despesas r
LEFT JOIN dim_fornecedor f
    ON f.cnpj_cpf_fornecedor = r.cnpj_cpf_fornecedor
   AND f.nome_fornecedor = r.nome_fornecedor
LEFT JOIN dim_categoria_despesa c
    ON c.tipo_despesa = r.tipo_despesa
JOIN dim_tempo t
    ON t.ano = r.ano AND t.mes = r.mes
ON CONFLICT (deputado_id, cod_documento, num_documento) DO NOTHING;
