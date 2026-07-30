# Projeto Lupa

Painel público de transparência sobre gastos (CEAP) e atuação de deputados federais, construído sobre a [API de Dados Abertos da Câmara dos Deputados](https://dadosabertos.camara.leg.br/swagger/api.html).

> ⚠️ Projeto em construção — módulo 3 de 12. Ver estado atual em [CLAUDE.md](CLAUDE.md).

## O que é

Um painel onde qualquer pessoa busca um deputado e sai com: quanto ele gastou, como isso se compara aos pares, e se há algum padrão de gasto que mereça checagem adicional — sempre com a explicação ao lado do número.

Leia o [Data Product Brief](docs/data_product_brief.md) para a definição completa de público-alvo, métrica norte e guardrails.

## Um princípio inegociável

O dado é público e oficial, mas o produto nomeia pessoas reais. Por isso:
- Nunca usamos "fraude" ou "corrupção" — o termo correto é **gasto atípico** ou **despesa sinalizada para checagem**.
- Toda sinalização vem com explicação (SHAP), nunca só o número.
- O painel mantém disclaimer permanente sobre fonte, atualização e o que "sinalizado" significa.

Detalhes completos em [docs/principios_responsabilidade.md](docs/principios_responsabilidade.md).

## Arquitetura

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

## Jornada (módulo a módulo)

| Módulo | Entrega |
|---|---|
| 1. Dados, IA e Negócio | Data Product Brief, princípios de responsabilidade |
| 2. SQL para Cientistas de Dados | Ingestão da API, star schema no Postgres, views de KPI |
| 3. Python para Cientistas de Dados | EDA em pandas, primeiras visualizações |
| 4. Estatística e Inferência | Intervalos de confiança, teste A/B simulado |
| 5. Fundamentos de ML | Target `houve_glosa`, split out-of-time, balanceamento |
| 6. Modelos Supervisionados | Comparativo de classificadores, análise de custo |
| 7. Ensembles e Explicabilidade | XGBoost/LightGBM/CatBoost + SHAP, MLflow |
| 8. Não Supervisionado e Anomalias | Clustering de perfis de gasto, detecção de outliers |
| 9. Redes Neurais | MLP, CNN, LSTM |
| 10. RAG e Fine-Tuning | Assistente sobre proposições legislativas |
| 11. Engenharia de Software | Pacote `src/lupa/`, testes, API FastAPI, CI |
| 12. MLOps | Docker Compose, CD, monitoramento de drift |
| Final | Painel público (Streamlit/Power BI) |

## Principais achados até aqui

Análise sobre 640.518 despesas de 512 deputados (2022 até hoje, R$ 801,7 milhões no total). Lista completa em [docs/eda_findings.md](docs/eda_findings.md).

1. O ranking de gasto individual é dominado por um confundidor geográfico — deputados de UFs distantes/grandes lideram por causa de deslocamento, não necessariamente por comportamento irregular.
2. Gasto total por partido reflete tamanho de bancada; comparação justa exige normalizar pelo número de deputados.
3. Companhias aéreas concentram gasto, mas aparecem fragmentadas sob nomes diferentes por falta de CNPJ em despesas de passagem — um problema de qualidade de dado sistemático, não aleatório.
4. Valores negativos existem (10.142 despesas) e têm explicação mundana: estornos de tarifa aérea, não erro ou irregularidade.
5. A regra clássica de outlier (1,5×IQR) sinaliza 10% do dado como "atípico" — volume alto demais pra ser útil, por causa da assimetria natural do gasto. Detecção de anomalia vai exigir métodos mais sofisticados (Módulo 8).

## Como rodar

_A definir a partir do módulo 2 (ingestão + Postgres via Docker)._

## Fonte de dados

API de Dados Abertos da Câmara dos Deputados — pública, gratuita, sem token necessário. [Swagger](https://dadosabertos.camara.leg.br/swagger/api.html)
