# Otimização de queries — Módulo 2

## Contexto

Testamos `EXPLAIN ANALYZE` em dois cenários diferentes sobre `fact_despesas` (640.518 linhas), pra entender quando um índice ajuda de verdade e quando não ajuda.

## Caso 1 — agregação sobre a tabela inteira (índice NÃO ajudou)

Query: somar o total recebido por fornecedor, sem nenhum filtro (base da view `vw_top10_fornecedores`).

- **Antes de qualquer índice em `id_fornecedor`:** `Parallel Seq Scan on fact_despesas`, 597.86ms
- **Depois de criar `idx_fact_despesas_fornecedor`:** ainda `Parallel Seq Scan`, 531.02ms (sem melhora relevante)

**Por quê:** quando a query precisa ler e agregar **100% das linhas da tabela** (não há `WHERE` filtrando um subconjunto), um *sequential scan* já é o plano ideal — o Postgres precisaria visitar toda a tabela de qualquer forma, e passar por um índice pra depois ainda ir buscar cada linha no disco (`Bitmap Heap Scan`) seria **mais lento**, não mais rápido. O planner do Postgres reconhece isso e ignora o índice de propósito.

O gargalo real aqui é o `Sort Method: external merge Disk` — o agrupamento por `nome_fornecedor, cnpj_cpf_fornecedor` (texto) em 640 mil linhas excede a memória de trabalho (`work_mem`) padrão e derrama pra disco. Isso não se resolve com índice, se resolve ajustando `work_mem` da sessão — fora do escopo deste módulo, registrado aqui como próximo passo possível.

## Caso 2 — busca filtrada por um fornecedor específico (índice ajudou muito)

Query: todas as despesas de um fornecedor específico (`WHERE id_fornecedor = 2951`, a TAM) — o tipo de busca que o painel público faria ao mostrar o "perfil" de um fornecedor.

- **Antes do índice:** `Parallel Seq Scan`, `Rows Removed by Filter: 213499`, **42.938ms**
- **Depois do índice `idx_fact_despesas_fornecedor`:** `Bitmap Index Scan`, **0.139ms**

**Melhora: ~300x mais rápido.**

**Por quê:** aqui a query só precisa de **22 linhas entre 640 mil** — um caso extremamente seletivo. Sem índice, o Postgres é obrigado a olhar linha por linha pra saber quais batem com o filtro. Com o índice, ele localiza diretamente as linhas certas sem varrer o resto.

## Lição geral

Índice **não é sempre bom** — ele ajuda quando a query é seletiva (busca um subconjunto pequeno), e pode ser ignorado (corretamente) pelo planner quando a query precisa da tabela inteira de qualquer forma. `EXPLAIN ANALYZE` antes e depois é o que permite essa decisão ser baseada em dado real, não em intuição.

## Achado adicional (não corrigido agora, fica pro Módulo 3)

Durante os testes, descobrimos que `dim_fornecedor` tem **4 registros distintos para "TAM"**, porque `cnpj_cpf_fornecedor` vem vazio para essa fornecedora, e uma restrição `UNIQUE` no Postgres não considera dois valores `NULL` como iguais — cada despesa sem CNPJ virou, na prática, um "fornecedor novo" na dimensão. As views de KPI não foram afetadas (o `GROUP BY` trata `NULL`s como iguais entre si), mas uma busca direta por `id_fornecedor` específico so retorna a fatia daquele id, não o fornecedor "TAM" como um todo. Isso é exatamente o problema de "nomes de fornecedor grafados de formas diferentes / CNPJ ausente" que o Módulo 3 da trilha já antecipa tratar.
