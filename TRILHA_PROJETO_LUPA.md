# Projeto Lupa — trilha passo a passo

Painel público de transparência sobre gastos (CEAP) e atuação de deputados federais, construído sobre a API pública da Câmara dos Deputados. Um único projeto evolutivo do módulo 1 ao 12 — cada etapa entrega um incremento real sobre a anterior, no mesmo repositório.

Ferramentas aparecem em **negrito** na primeira vez que entram em cena, com a fonte oficial e um recurso extra de estudo logo abaixo do bloco "Ferramentas desta etapa" de cada módulo. Pule a etapa de estudo de qualquer ferramenta que você já domina.

---

## Um adendo sobre responsabilidade — leia antes de divulgar

O dado é público e oficial, mas o produto final nomeia pessoas reais — isso muda o padrão de cuidado:

1. Nunca use "fraude" ou "corrupção" sem apuração jornalística ou decisão judicial. O termo correto é **gasto atípico** ou **despesa sinalizada para checagem**.
2. Toda sinalização exibida vem com a explicação (**SHAP**) ao lado — nunca só o número.
3. Mantenha um disclaimer permanente no painel: fonte oficial, data da última atualização, e o que "sinalizado" significa.

---

## A fonte de dados

**API de Dados Abertos da Câmara dos Deputados** — pública, gratuita, sem token, atualizada continuamente.
Fonte oficial: [Swagger da API](https://dadosabertos.camara.leg.br/swagger/api.html)

Endpoints principais:
- `/deputados` — lista de deputados (id, nome, partido, UF)
- `/deputados/{id}/despesas` — despesas da CEAP desde 2008 (tipo, fornecedor, CNPJ, valor, `valorGlosa`)
- `/proposicoes` e `/proposicoes/{id}` — projetos de lei e ementas

---

## Estrutura do repositório

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

---

## Módulo 1 — Dados, IA e Negócio

**Contexto:** antes de codar, defina o produto — um painel público de transparência, com uma responsabilidade a mais: vai nomear pessoas reais.

**Ferramentas desta etapa:**
- **CRISP-DM** — framework que estrutura o projeto do problema de negócio ao deploy. Fonte: [CRISP-DM Guide](https://www.datascience-pm.com/crisp-dm-2/)

**Passo a passo:**
1. Escreva um Data Product Brief de 1 página: público-alvo e a pergunta central que o painel responde.
2. Defina a métrica norte (ex.: cobertura dos 513 deputados, tempo de resposta da busca) e os guardrails (latência máxima, nunca sinalizar sem explicação).
3. Escreva o documento de princípios de responsabilidade — as regras editoriais do adendo acima, formalizadas antes de qualquer dado ir ao ar.
4. Aplique o **CRISP-DM** adaptado: mapeie as 6 fases para o que você vai fazer em cada módulo seguinte.
5. Crie o repositório GitHub (`lupa-camara`) com README esqueleto.

**Entregável:** `docs/data_product_brief.md`, `docs/principios_responsabilidade.md`, repositório publicado.

**Critério de sucesso:** métrica norte mensurável e justificada; regras de responsabilidade escritas antes de qualquer dado público.

**Pergunta de entrevista:** *"Como você definiria o escopo de um produto de dados que expõe informação pública sobre pessoas reais?"*

---

## Módulo 2 — SQL para Cientistas de Dados

**Ferramentas desta etapa:**
- **API da Câmara dos Deputados** — fonte de todo o dado. [Swagger](https://dadosabertos.camara.leg.br/swagger/api.html)
- **PostgreSQL** — banco relacional. [Docs](https://www.postgresql.org/docs/) · extra: [PostgreSQL Tutorial](https://www.postgresqltutorial.com/)
- **Docker** — sobe o Postgres localmente. [Get Started](https://docs.docker.com/get-started/)
- **SQL** (fundamentos e window functions) — [Kaggle Learn: Intro to SQL](https://www.kaggle.com/learn/intro-to-sql) · [Kaggle Learn: Advanced SQL](https://www.kaggle.com/learn/advanced-sql)

**Passo a passo:**
1. Escreva um script de ingestão que percorre a **API da Câmara** com paginação, trata erros e evita duplicar dado ao rodar de novo.
2. Suba os dados brutos em **PostgreSQL** rodando via **Docker**.
3. Modele um star schema em **SQL**: `fact_despesas`, `dim_deputado`, `dim_fornecedor`, `dim_categoria_despesa`, `dim_tempo`.
4. Escreva window functions: ranking de deputados por gasto (`RANK`), média móvel de 3 meses (`AVG OVER RANGE`), variação mês a mês (`LAG`).
5. Crie views de KPI: gasto total por deputado/partido/UF, ticket médio por categoria, top 10 fornecedores.
6. Rode `EXPLAIN ANALYZE` na query mais pesada e otimize com índice — documente antes/depois.

**Entregável:** `src/ingest.py`, `sql/schema.sql`, `sql/views/`, `docs/query_optimization.md`.

**Critério de sucesso:** ingestão idempotente (rodar 2x não duplica); views batendo com checagem manual; otimização documentada.

**Pergunta de entrevista:** *"Como você projetaria a ingestão de uma API paginada de forma incremental, sem duplicar dado?"*

---

## Módulo 3 — Python para Cientistas de Dados

**Ferramentas desta etapa:**
- **Pandas** — [Docs](https://pandas.pydata.org/docs/) · extra: [Kaggle Learn: Pandas](https://www.kaggle.com/learn/pandas)
- **NumPy** — [Quickstart](https://numpy.org/doc/stable/user/quickstart.html)
- **Matplotlib / Seaborn / Plotly** — [Matplotlib Tutorials](https://matplotlib.org/stable/tutorials/index.html) · [Seaborn Tutorial](https://seaborn.pydata.org/tutorial.html)
- **uv** (ou Poetry) — [uv Docs](https://docs.astral.sh/uv/) · [Poetry Docs](https://python-poetry.org/docs/)

**Passo a passo:**
1. Monte o ambiente reprodutível com **uv** (ou Poetry).
2. Carregue os dados do Postgres com **Pandas** e explore com **NumPy**: distribuição de gasto por categoria/partido/UF, ranking dos 20 que mais gastaram, evolução mensal.
3. Trate inconsistências reais: nomes de fornecedor grafados de formas diferentes, CNPJ ausente, outliers genuínos.
4. Construa 5+ visualizações com **Matplotlib**, **Seaborn** e/ou **Plotly** no padrão de relatório.
5. Atualize o README com os 5 achados mais interessantes.

**Entregável:** `pyproject.toml`, `notebooks/01_eda.ipynb`, `docs/eda_findings.md`.

**Critério de sucesso:** ambiente reproduzível em um comando; achados vão além do óbvio; decisões de limpeza documentadas.

**Pergunta de entrevista:** *"Como você lida com inconsistência de identificadores sem uma chave única confiável?"*

---

## Módulo 4 — Decisão com Dados: Estatística, Inferência e Testes A/B

**Ferramentas desta etapa:**
- **SciPy.stats** — [Reference](https://docs.scipy.org/doc/scipy/reference/stats.html)
- **statsmodels** — [Docs](https://www.statsmodels.org/stable/index.html)
- Intuição estatística — extra: [StatQuest (YouTube)](https://www.youtube.com/@statquest)

**Passo a passo:**
1. Calcule intervalos de confiança para o gasto médio por deputado e categoria com **SciPy.stats**.
2. Teste se o gasto médio difere entre partidos/regiões — documente o confundidor geográfico (UFs grandes gastam mais com passagem por geografia, não comportamento) com **statsmodels**.
3. Desenhe um teste A/B simulado: mudança de teto de reembolso de uma categoria, com MDE e tamanho de amostra calculados.
4. Simule dados de controle/tratamento com **NumPy**, rode o teste e escreva a conclusão em linguagem de gestão pública.

**Entregável:** `notebooks/02_inferencia_estatistica.ipynb`, `docs/confundidor_geografico.md`, `docs/ab_test_design.md`.

**Critério de sucesso:** confundidor demonstrado com números; cálculo de amostra sensível ao MDE.

**Pergunta de entrevista:** *"Me dá um exemplo real de correlação que parecia causal mas tinha confundidor."*

---

## Módulo 5 — Fundamentos de Machine Learning

**Ferramentas desta etapa:**
- **scikit-learn** (pré-processamento) — [Preprocessing Docs](https://scikit-learn.org/stable/modules/preprocessing.html)
- **imbalanced-learn** (SMOTE) — [Docs](https://imbalanced-learn.org/stable/)
- Fundamentos de ML — extra: [Kaggle Learn: Intro to ML](https://www.kaggle.com/learn/intro-to-machine-learning) · [Intermediate ML](https://www.kaggle.com/learn/intermediate-machine-learning)

**Passo a passo:**
1. Crie a coluna binária `houve_glosa` a partir de `valorGlosa` e meça a proporção real — não assuma o desbalanceamento.
2. Construa o pipeline de pré-processamento com **scikit-learn**: scaling, encoding, tratamento de ausentes.
3. Faça o split out-of-time por `dataDocumento` — nunca aleatório, porque o teto de categoria muda ano a ano.
4. Compare estratégias de balanceamento com **imbalanced-learn** (SMOTE, undersampling, class_weight).
5. Escreva um teste comprovando ausência de data leakage.

**Entregável:** `src/preprocessing.py`, `docs/target_e_balanceamento.md`.

**Critério de sucesso:** proporção real de glosa medida; split cronológico comprovado; sem leakage.

**Pergunta de entrevista:** *"Como você definiria o target quando não existe um rótulo óbvio?"*

---

## Módulo 6 — Modelos Supervisionados

**Ferramentas desta etapa:**
- **scikit-learn** (supervised learning) — [Docs](https://scikit-learn.org/stable/supervised_learning.html)

**Passo a passo:**
1. Treine Regressão Logística, KNN, Naive Bayes e SVM com **scikit-learn**, prevendo `houve_glosa`, mesmo split out-of-time.
2. Calcule precision, recall, F1, AUC-ROC, KS e PR-AUC — priorize PR-AUC dado o desbalanceamento.
3. Construa uma tabela de custo: falso positivo (sinalizar despesa legítima) vs falso negativo (deixar passar).
4. Interprete os coeficientes da logística em odds ratio.

**Entregável:** `notebooks/03_modelos_supervisionados.ipynb`, `docs/comparativo_modelos.md`.

**Critério de sucesso:** escolha do modelo amarrada ao custo, não só à métrica.

**Pergunta de entrevista:** *"Por que acurácia é ruim aqui, e por que existe a PR-AUC?"*

---

## Módulo 7 — Modelos Avançados, Ensembles e Explicabilidade

**Ferramentas desta etapa:**
- **MLflow** — [Docs](https://mlflow.org/docs/latest/index.html)
- **XGBoost** — [Docs](https://xgboost.readthedocs.io/)
- **LightGBM** — [Docs](https://lightgbm.readthedocs.io/)
- **CatBoost** — [Docs](https://catboost.ai/docs/)
- **Optuna** — [Docs](https://optuna.readthedocs.io/)
- **SHAP** — [Docs](https://shap.readthedocs.io/)

**Passo a passo:**
1. Configure o **MLflow** Tracking e registre todo experimento a partir daqui.
2. Treine **XGBoost**, **LightGBM** e **CatBoost** com tuning via **Optuna**.
3. Promova o melhor modelo no Model Registry do **MLflow**.
4. Gere explicações com **SHAP** — globais e locais (3 despesas reais), em linguagem acessível.
5. Ajuste threshold pela curva PR e calibre as probabilidades.

**Entregável:** experimentos no MLflow (15+ runs), `docs/shap_report.md`, `docs/threshold_calibration.md`.

**Critério de sucesso:** modelo versionado no registry; explicação SHAP sem jargão; threshold não é 0.5 padrão.

**Pergunta de entrevista:** *"Como você explicaria pra um jornalista por que o modelo sinalizou uma despesa?"*

---

## Módulo 8 — Aprendizado Não Supervisionado e Detecção de Anomalias

**Ferramentas desta etapa:**
- **scikit-learn** (clustering e outlier detection) — [Clustering](https://scikit-learn.org/stable/modules/clustering.html) · [Outlier Detection](https://scikit-learn.org/stable/modules/outlier_detection.html)
- **UMAP** — [Docs](https://umap-learn.readthedocs.io/)
- **HDBSCAN** — [Docs](https://hdbscan.readthedocs.io/)

**Passo a passo:**
1. Reduza a dimensionalidade com PCA e **UMAP**, visualize o espaço de despesas.
2. Segmente perfis de gasto com K-Means e **HDBSCAN** (via **scikit-learn** + HDBSCAN).
3. Aplique Isolation Forest e Local Outlier Factor (**scikit-learn**) sem usar `houve_glosa`.
4. Revele o rótulo real só ao final e calcule precision/recall da abordagem "cega".

**Entregável:** `notebooks/04_nao_supervisionado.ipynb`, `docs/perfis_de_gasto.md`, `docs/deteccao_anomalias_vs_glosa.md`.

**Critério de sucesso:** clusters com narrativa de negócio; avaliação contra rótulo real documentada.

**Pergunta de entrevista:** *"Como detectar um padrão irregular sem nenhum histórico rotulado?"*

---

## Módulo 9 — Redes Neurais e Modelos Generativos (bases)

**Ferramentas desta etapa:**
- **PyTorch** — [60 Minute Blitz](https://pytorch.org/tutorials/beginner/basics/intro.html)
- **Hugging Face Transformers** — [Docs](https://huggingface.co/docs/transformers/index) · extra: [NLP Course (grátis)](https://huggingface.co/learn/nlp-course)

**Passo a passo:**
1. Treine um MLP em **PyTorch** prevendo glosa; compare honestamente com o XGBoost do módulo 7.
2. Complete os laboratórios de CNN (transfer learning) e Autoencoders com Fashion MNIST.
3. Treine uma LSTM prevendo o gasto do próximo mês de um deputado, a partir do histórico mensal real.
4. Bônus: classificador de texto simples com **Hugging Face Transformers** sobre descrição de despesa ou ementa de proposição.

**Entregável:** notebooks de MLP, CNN/Autoencoders e LSTM; `docs/quando_usar_deep_learning.md`.

**Critério de sucesso:** comparação MLP vs XGBoost justa; análise crítica honesta.

**Pergunta de entrevista:** *"Onde deep learning fez sentido neste projeto e onde foi over-engineering?"*

---

## Módulo 10 — IA Generativa: RAG e Fine-Tuning

**Ferramentas desta etapa:**
- **RAG** (fundamentos) — extra: [Activeloop RAG Course (grátis)](https://learn.activeloop.ai/courses/rag)
- **LangChain** — [Docs](https://python.langchain.com/docs/introduction/)
- **LlamaIndex** — [Docs](https://docs.llamaindex.ai/)
- **Hugging Face PEFT** (LoRA/QLoRA) — [Docs](https://huggingface.co/docs/peft/index) · extra: [LoRA and PEFT (grátis)](https://huggingface.co/learn/smol-course/unit1/3a)

**Passo a passo:**
1. Monte o pipeline de **RAG** com **LangChain** (ou **LlamaIndex**): chunking das proposições, indexação, retrieval, geração.
2. Implemente confidence scoring e fallback — o sistema admite quando não sabe.
3. Avalie com faithfulness/relevância em 15+ perguntas reais (ex.: "o que o deputado X propôs sobre educação?").
4. Como exercício separado, rode fine-tuning com **Hugging Face PEFT** (LoRA/QLoRA), comparando com prompt engineering puro.

**Entregável:** `src/rag_pipeline.py`, `docs/rag_eval.md`, `notebooks/08_finetuning_lora.ipynb`.

**Critério de sucesso:** RAG responde com citação da fonte real; recusa quando não sabe.

**Pergunta de entrevista:** *"Como medir se o RAG está inventando uma proposição?"*

---

## Módulo 11 — Software Engineering para Cientistas de Dados

**Ferramentas desta etapa:**
- **CookieCutter Data Science** — [Docs](https://cookiecutter-data-science.drivendata.org/)
- **pytest** — [Docs](https://docs.pytest.org/)
- **ruff** — [Docs](https://docs.astral.sh/ruff/)
- **black** — [Docs](https://black.readthedocs.io/)
- **FastAPI** — [Tutorial](https://fastapi.tiangolo.com/tutorial/)
- **Pydantic** — [Docs](https://docs.pydantic.dev/latest/)
- **GitHub Actions** — [Docs](https://docs.github.com/actions)

**Passo a passo:**
1. Refatore o notebook em pacote Python (padrão **CookieCutter Data Science**), classes para ingestão, features, modelo, explicador.
2. Escreva testes com **pytest**: unitários + integração ponta a ponta.
3. Configure **ruff** e **black**, adicione type hints.
4. Configure **GitHub Actions**: testes e lint a cada pull request.
5. Construa a API com **FastAPI** + **Pydantic**: endpoint `/deputado/{nome}/resumo` retornando gasto, ranking, cluster, risco de glosa explicado e proposições recentes.

**Entregável:** `src/lupa/` instalável, `tests/`, `.github/workflows/ci.yml`, `api/main.py`.

**Critério de sucesso:** `pip install -e .` funciona; CI verde; endpoint consolidado responde tudo num payload.

**Pergunta de entrevista:** *"Como desenhar uma API que consolida vários modelos num único endpoint?"*

---

## Módulo 12 — MLOps: Produtização, Monitoramento e Retreino

**Ferramentas desta etapa:**
- **Docker Compose** — [Docs](https://docs.docker.com/compose/)
- **GitHub Actions** (CD) — [Deployment Docs](https://docs.github.com/actions/deployment)
- **Evidently AI** — [Docs](https://docs.evidentlyai.com/)
- **Cloud free tier** — [AWS Free Tier](https://aws.amazon.com/free/) · [Render Docs](https://render.com/docs)

**Passo a passo:**
1. Containerize com Docker (multi-stage) e orquestre com **Docker Compose**.
2. Configure CI/CD no **GitHub Actions** com triggers de retreino (tempo, volume de dado novo, drift).
3. Implemente monitoramento de data drift e concept drift com **Evidently AI**.
4. Simule drift de propósito e confirme que o alerta dispara.
5. Faça deploy em **cloud free tier** com URL pública; documente champion/challenger.

**Entregável:** `docker/`, `.github/workflows/cd.yml`, `docs/monitoramento_drift.md`, URL pública.

**Critério de sucesso:** serviço responde com dado real; drift simulado dispara alerta com prova.

**Pergunta de entrevista:** *"Como adaptar o retreino para um evento previsível como uma nova legislatura?"*

---

## Entregável final — o painel público

**Ferramentas desta etapa:**
- **Power BI** — [Docs](https://learn.microsoft.com/power-bi/)
- **Streamlit** — [Docs](https://docs.streamlit.io/)
- **Plotly Dash** — [Docs](https://dash.plotly.com/)

**Passo a passo:**
1. Escolha **Power BI** (plugado na API via Power Query) ou um app web com **Streamlit**/**Plotly Dash** — os dois é ainda melhor pra portfólio.
2. Implemente: busca por nome com autocomplete, ranking de quem mais gastou, evolução no tempo, perfil de cluster, despesas sinalizadas com SHAP ao lado, acesso ao assistente RAG.
3. Coloque o disclaimer permanente e visível.
4. Teste pessoalmente 10+ nomes diferentes antes de divulgar.

**Critério de sucesso:** alguém de fora abre o link, busca qualquer deputado e sai com resposta completa e correta.

---

## Ordem de prioridade se o tempo apertar

SQL e Python (módulos 2-3) nunca cortam — é a base. ML clássico com explicabilidade (módulos 5-7) vem em seguida, é o que mais cai em entrevista. Deep learning e GenAI (módulos 9-10) podem ter menos profundidade, mas não pule o RAG — é o que o mercado mais pede agora. Engenharia e MLOps (módulos 11-12) podem vir por último, mas são o que separa portfólio de exercício de curso — não corte.

## Checklist final de portfólio

- README mestre contando a jornada: problema → arquitetura → decisões → painel público.
- Case study de 1-2 páginas no formato Situação / Tarefa / Ação / Resultado.
- ADRs documentando decisões técnicas e editoriais.
- CI verde, testes passando, API documentada, modelo no Model Registry.
- Painel público no ar, com disclaimer e monitoramento de drift configurado.
- Você defende, em voz alta e sem notas, cada decisão do projeto.
