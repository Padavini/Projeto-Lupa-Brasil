# Perfis de gasto dos deputados — Módulo 8

Segmentação de 511 deputados por **estilo** de gasto (proporção do total em cada categoria, não o valor absoluto), usando PCA/UMAP para visualização e K-Means/HDBSCAN para agrupar.

## Redução de dimensionalidade

PCA em 2 componentes explica 35,2% da variância — moderado, esperado dado que o perfil tem 9 dimensões (8 categorias + gasto total). UMAP usado em paralelo para uma visualização não-linear complementar.

## K-Means (k=4) — as 4 personas de gasto

**Decisão sobre k:** o silhouette score ficou baixo e quase empatado entre todos os valores testados (0,13-0,17), sinal de que o gasto parlamentar não forma grupos naturalmente bem separados — é mais um contínuo de comportamento do que categorias distintas. k=2 venceu tecnicamentre, mas escolhemos **k=4** por revelar uma narrativa de negócio mais interpretável, com silhouette ainda razoável (0,153).

| Cluster | N | Gasto médio | Perfil dominante |
|---|---|---|---|
| **0 — "Perfil viajante"** | 63 | R$ 896 mil | 42,3% do gasto em passagem aérea — muito acima da média dos outros grupos |
| **1 — "Perfil divulgador"** | 197 | R$ 1,62 milhão | 55,5% do gasto em divulgação da atividade parlamentar — o maior gasto médio total |
| **2 — "Perfil operacional"** | 250 | R$ 1,71 milhão | Mais equilibrado: 20,5% locação de veículo, 18,4% manutenção de escritório, 16,3% passagem aérea |
| **3 — "Caso isolado"** | 1 | R$ 679 | 100% do gasto (mínimo) em telefonia — deputado com volume de despesa quase nulo, capturado pelo K-Means como grupo próprio por ser um extremo isolado |

**Achado de negócio:** o cluster 3 (n=1) é, na prática, o próprio K-Means "descobrindo" um outlier sozinho — um deputado cujo padrão de gasto é tão diferente (quase zero) que forma seu próprio grupo. Isso ilustra um limite do K-Means: ele sempre distribui todos os pontos em k grupos, mesmo quando um deles é claramente um caso isolado, não uma "categoria" de verdade.

## HDBSCAN — só 52 de 511 deputados formam grupos densos

Ao contrário do K-Means (que força todo mundo num grupo), o HDBSCAN encontrou apenas **2 clusters pequenos e densos**, classificando **459 dos 511 deputados (89,8%) como "ruído"** — sem padrão de gasto denso o suficiente pra formar um grupo.

**Isso não é falha do método — é informação real:** confirma o que o silhouette baixo já sugeria. A maioria dos deputados tem um perfil de gasto único o suficiente para não se encaixar perfeitamente em nenhum "arquétipo" — reforçando, mais uma vez, por que o painel nunca deveria tratar "não se encaixar no padrão" como sinal de irregularidade. Aqui, "não se encaixar" é a **norma**, não a exceção.
