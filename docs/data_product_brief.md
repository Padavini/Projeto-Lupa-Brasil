# Data Product Brief — Projeto Lupa

## O que é

Painel público de transparência sobre gastos parlamentares (CEAP) e atuação de deputados federais, construído sobre a API pública da Câmara dos Deputados.

## Público-alvo

- **Jornalistas de dados e fact-checkers** — precisam de números confiáveis e rastreáveis para reportagem.
- **Cidadãos engajados** — querem consultar o próprio deputado ou comparar deputados/partidos/UFs.
- **Recrutadores e pares técnicos** (contexto de portfólio) — avaliam a solidez técnica do pipeline, não só a UI.

## Pergunta central que o painel responde

> "Como um deputado específico gastou o dinheiro público da cota parlamentar (CEAP), como isso se compara a seus pares, e existe algum padrão de gasto que mereça checagem adicional?"

O painel não responde "esse deputado é corrupto?" — essa pergunta está fora de escopo por design (ver `principios_responsabilidade.md`).

## Métrica norte

**Cobertura completa dos 513 deputados em exercício com dado atualizado**, medida como:

```
cobertura = deputados_com_dados_completos / 513
```

Justificativa: é a métrica mais honesta para um produto de transparência — de nada adianta um modelo sofisticado se o painel não cobre todo o universo de deputados que o usuário espera encontrar. Cobertura parcial mina a confiança no produto inteiro (usuário busca um nome, não encontra, abandona).

**Métrica secundária:** tempo de resposta da busca por deputado (p95 < 2s), porque a experiência de "buscar um nome e sair com resposta completa" é o critério de sucesso do painel final (ver trilha, entregável final).

## Guardrails

- **Latência máxima:** p95 de 2s para o endpoint de resumo do deputado.
- **Nunca sinalizar sem explicação:** toda despesa marcada como atípica vem com SHAP ao lado — sem exceção, sem "modo debug" que mostre só o score.
- **Nunca usar "fraude"/"corrupção":** ver princípios de responsabilidade.
- **Dado sempre rastreável à fonte oficial:** todo número exibido deve ser reproduzível a partir da API da Câmara — sem transformação opaca.
- **Falha visível, não silenciosa:** se a ingestão falhar ou o dado estiver desatualizado, o painel deve mostrar isso (data da última atualização), não mascarar com dado velho sem aviso.

## CRISP-DM adaptado à trilha do projeto

| Fase CRISP-DM | O que significa aqui | Módulos |
|---|---|---|
| **Business Understanding** | Definir público-alvo, pergunta central, métrica norte e guardrails éticos | Módulo 1 |
| **Data Understanding** | Explorar a API da Câmara, entender schema, qualidade e limitações do dado (sem rótulo de fraude, `valorGlosa` como único sinal objetivo) | Módulos 2-3 |
| **Data Preparation** | Ingestão idempotente, star schema, limpeza de fornecedor/CNPJ, engenharia do target `houve_glosa`, split out-of-time | Módulos 2-3, 5 |
| **Modeling** | Modelos supervisionados (classificação de glosa), não supervisionados (clustering, anomalias), deep learning, RAG | Módulos 6-10 |
| **Evaluation** | Métricas amarradas a custo de negócio (PR-AUC, tabela de custo FP/FN), explicabilidade SHAP, avaliação de RAG (faithfulness) | Módulos 6-10 |
| **Deployment** | Pacote Python, API FastAPI, containerização, CI/CD, monitoramento de drift, painel público | Módulos 11-12, entregável final |

O ciclo não é estritamente linear: a cada módulo há retorno a Data Understanding/Preparation conforme novos problemas de dado aparecem (ex.: novo confundidor descoberto no módulo 4 pode exigir nova feature no módulo 5).

## Fora de escopo (v1)

- Acusação ou julgamento de conduta — o painel sinaliza padrões estatísticos, não veredictos.
- Dados de outras casas legislativas (Senado, assembleias estaduais) — fica para uma iteração futura.
- Previsão de voto ou intenção política — fora do escopo de gasto/atuação.
