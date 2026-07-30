# Projeto Lupa

Painel público de transparência sobre gastos (CEAP) e atuação de deputados federais, construído sobre a API pública da Câmara dos Deputados. Nasceu como projeto de portfólio da pós-graduação em Data Science + IA (Diego Padavini), mas é tratado com padrão de produção real desde o módulo 1 — o plano é publicar e divulgar o painel ao final.

Trilha completa (12 módulos, desafio + entregável + critério de sucesso por módulo) e o guia de fontes de estudo por ferramenta estão fora deste repositório — cole o conteúdo relevante em `docs/` conforme for avançando, ou referencie os arquivos originais.

## Princípios inegociáveis — ler antes de qualquer PR

O dado é público e oficial, mas o produto nomeia pessoas reais. Isso muda o padrão de cuidado:

- Nunca usar "fraude" ou "corrupção" em código, commit, docstring ou UI. O termo correto é "gasto atípico" ou "despesa sinalizada para checagem".
- Toda sinalização exibida (score de risco, cluster, anomalia) vem acompanhada da explicação (SHAP) — nunca só o número.
- O painel público mantém disclaimer permanente e visível: fonte oficial dos dados, data da última atualização, e o que "sinalizado" significa (e não significa).
- Antes de mergear qualquer feature que afete o que é exibido publicamente, revisar se ela respeita essas três regras.

## Fonte de dados

API: `https://dadosabertos.camara.leg.br` — pública, sem token, paginada, atualizada continuamente.

Endpoints principais:
- `/deputados` — lista de deputados (id, nome, partido, UF)
- `/deputados/{id}/despesas` — despesas da CEAP desde 2008 (tipo, fornecedor, CNPJ, valor, `valorGlosa`)
- `/proposicoes` e `/proposicoes/{id}` — projetos de lei e ementas

Coluna-chave: `valorGlosa` — quando a própria Câmara reprova parte de uma despesa. É a base do target de ML do projeto: `houve_glosa = valorGlosa > 0`. Não existe rótulo de fraude no dado — não inventar um.

## Arquitetura por camada

1. **Ingestão & armazenamento** — script de ingestão paginado da API → PostgreSQL (Docker). Star schema: `fact_despesas`, `dim_deputado`, `dim_fornecedor`, `dim_categoria_despesa`, `dim_tempo`.
2. **Análise & estatística** — Python/Pandas para EDA; SciPy/statsmodels para inferência.
3. **Modelagem preditiva** — scikit-learn → XGBoost/LightGBM/CatBoost (MLflow tracking) → não supervisionado (PCA/UMAP, clustering, Isolation Forest) → deep learning (PyTorch) → RAG sobre proposições (módulo 10).
4. **Engenharia de software** — pacote Python instalável (`src/lupa/`), testes com pytest, FastAPI servindo `/deputado/{nome}/resumo`.
5. **Deploy & produto** — Docker Compose, CI/CD via GitHub Actions, monitoramento de drift (Evidently), painel público em Power BI ou Streamlit.

## Estrutura de pastas

```
lupa-camara/
  data/            (raw/, processed/ — no .gitignore)
  notebooks/
  sql/             (schema.sql, views/)
  src/lupa/        (pacote Python — a partir do módulo 11)
  api/             (FastAPI — módulo 11)
  docker/          (módulo 12)
  docs/            (Data Product Brief, princípios de responsabilidade, relatórios)
  tests/
  README.md
```

## Convenções de código

- Python formatado com `black`, lintado com `ruff`. Rodar os dois antes de commitar.
- Type hints em toda função pública.
- Commits semânticos (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`).
- Toda função de transformação de dado tem teste correspondente em `tests/` antes de ser considerada pronta.
- **Split de treino/teste é sempre out-of-time por `dataDocumento`** — nunca aleatório. As regras de teto de CEAP mudam ano a ano; um split aleatório vaza regra futura para o passado.
- Antes de reportar qualquer métrica de modelo, verificar ausência de data leakage.

## Estado atual

Atualizar esta seção conforme o projeto avança — é o que dá contexto de "onde estamos" a cada nova sessão.

- Módulo em andamento: **5 — Fundamentos de Machine Learning** (Módulos 1-4 concluídos)
- Último entregável concluído: Módulo 4 (Estatística e Inferência) — `notebooks/02_inferencia_estatistica.ipynb` com intervalos de confiança, `docs/confundidor_geografico.md` (distância até Brasília é estatisticamente significativa para gasto, partido sozinho não é a 5%) e `docs/ab_test_design.md` (teto de reembolso de combustível: com 512 deputados, MDE de 5-10% é inviável de detectar; simulação com MDE 20% ilustrou o conceito de poder estatístico/falso negativo na prática).
- Achado pendente (qualidade de dado, não resolvido): `dim_fornecedor`/nomes de fornecedor fragmentados para suppliers menores sem CNPJ (só as 3 maiores companhias aéreas foram normalizadas no Módulo 3).
- Próximo passo: Módulo 5 — criar target `houve_glosa`, pipeline de pré-processamento com scikit-learn, split out-of-time por `dataDocumento`, comparar balanceamento com imbalanced-learn.

## Como pedir ajuda aqui

Ao iniciar uma sessão, diga em qual módulo está e cole o trecho relevante do desafio (contexto, o que construir, critério de sucesso) se ainda não estiver em `docs/`. Peça implementação incremental — um módulo de cada vez, sem pular etapas de teste. Se uma decisão técnica for tomada (ex: por que XGBoost em vez de deep learning, por que esse threshold), registrar em `docs/decisoes_tecnicas.md` — vira material de entrevista depois.
