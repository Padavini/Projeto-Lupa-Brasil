# Target e balanceamento — Módulo 5

## O target: `houve_glosa`

Não existe rótulo de fraude no dado da API — o único sinal objetivo é `valorGlosa`, quando a própria Câmara reprova parte de uma despesa. O target é definido como:

```python
houve_glosa = valor_glosa > 0
```

## Proporção real (medida, não assumida)

```
com_glosa: 30.687
total:     640.518
proporção: 4,791%
```

Confirmado tanto via SQL direto quanto via `src/preprocessing.py`. O dataset é desbalanceado, mas não extremamente raro (4,8%, não 0,1%) — relevante pra escolha de métrica e estratégia nos módulos seguintes.

## Split out-of-time — nunca aleatório

Por que: as regras de teto de CEAP mudam ano a ano. Um split aleatório deixaria despesas de anos futuros "vazarem" informação (ex.: um novo teto de 2025) para o treino de um modelo que deveria simular o conhecimento disponível em 2023 — um caso clássico de data leakage temporal.

Implementado em `split_out_of_time(df, ano_corte, mes_corte)`: treino = tudo antes do corte; teste = do corte em diante. Testado (`tests/test_preprocessing.py`):
- `test_split_out_of_time_nao_sobrepoe_periodo` — comprova que o último período do treino é sempre anterior ao primeiro período do teste.
- `test_split_out_of_time_nao_e_aleatorio` — comprova que rodar o split duas vezes com o mesmo corte dá exatamente o mesmo resultado (determinístico, sem embaralhamento).

Split de exemplo usado (corte em abril/2026): **585.372 linhas de treino, 55.146 de teste**.

## Pipeline de pré-processamento

`construir_pipeline_preprocessamento()` (scikit-learn `ColumnTransformer`):
- **Numéricas** (`valor_documento`): imputação pela mediana (robusta a outliers, ver `docs/eda_findings.md`) + `StandardScaler`.
- **Categóricas** (`categoria`, `partido`, `uf`): imputação com categoria `"desconhecido"` + `OneHotEncoder` com `handle_unknown="ignore"` (para categorias que apareçam no teste mas não no treino, sem quebrar o pipeline).

## Prova de ausência de data leakage

`test_pipeline_ajustado_so_no_treino_nao_ve_dado_de_teste` comprova que o `StandardScaler` é ajustado (`fit`) **apenas com a média do treino**, nunca vendo o teste durante o ajuste — o teste falharia se, por engano, o pipeline fosse ajustado com o dataset inteiro antes do split (um erro comum e sutil de vazamento).

## Comparação de estratégias de balanceamento

Aplicadas sobre o treino já pré-processado (557.172 sem glosa vs 28.200 com glosa):

| Estratégia | Resultado | Trade-off |
|---|---|---|
| **Original** (sem balancear) | 557.172 / 28.200 | Desbalanceamento real preservado; modelo pode aprender a sempre prever "sem glosa" |
| **SMOTE** (oversampling sintético) | 557.172 / 557.172 | Preserva todo o dado majoritário, mas os exemplos minoritários novos são sintéticos (interpolados), podendo introduzir ruído |
| **Undersampling** (`RandomUnderSampler`) | 28.200 / 28.200 | Simples e sem dado sintético, mas descarta ~95% do dado majoritário (557.172 → 28.200) — perda de informação real |
| **`class_weight="balanced"`** | sem resample | Não altera os dados; ajusta a função de custo do próprio classificador (disponível em Regressão Logística, árvores, etc. no Módulo 6) — evita tanto ruído sintético quanto perda de dado |

Nenhuma estratégia foi "vencedora" definida ainda — a escolha final depende de como cada uma afeta a métrica de negócio (PR-AUC, tabela de custo FP/FN), o que é o foco do **Módulo 6**.
