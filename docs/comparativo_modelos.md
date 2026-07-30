# Comparativo de modelos supervisionados — Módulo 6

Target: `houve_glosa`. Split out-of-time (corte em abril/2026). Treino balanceado via `RandomUnderSampler` (56.400 linhas); teste mantido intacto, com a proporção real (4,51% de glosa, 55.146 linhas).

## Métricas (ordenadas por PR-AUC)

| Modelo | Precision | Recall | F1 | AUC-ROC | **PR-AUC** | KS |
|---|---|---|---|---|---|---|
| **KNN** | 0,181 | 0,789 | 0,294 | 0,880 | **0,321** | 0,620 |
| Regressão Logística | 0,160 | 0,770 | 0,264 | 0,841 | 0,262 | 0,590 |
| SVM (linear) | 0,157 | 0,772 | 0,261 | 0,840 | 0,259 | 0,590 |
| Naive Bayes | 0,058 | **0,951** | 0,110 | 0,658 | 0,065 | 0,298 |

**Por que PR-AUC, não acurácia:** um modelo que sempre previr "sem glosa" já acertaria ~95,5% (a proporção da classe majoritária) sem aprender nada. PR-AUC foca na capacidade de distinguir a classe minoritária (glosa), que é o que realmente importa aqui.

## Tabela de custo — o critério de decisão real

Custo assumido: **R$ 50** por falso positivo (analista revisando despesa legítima à toa) e **R$ 500** por falso negativo (despesa com glosa real não revisada) — refletindo que deixar passar uma irregularidade tem custo institucional maior que uma checagem desnecessária.

| Modelo | FP | FN | Custo FP | Custo FN | **Custo total** |
|---|---|---|---|---|---|
| **KNN** | 8.875 | 526 | R$ 443.750 | R$ 263.000 | **R$ 706.750** |
| Regressão Logística | 10.079 | 573 | R$ 503.950 | R$ 286.500 | R$ 790.450 |
| SVM (linear) | 10.298 | 567 | R$ 514.900 | R$ 283.500 | R$ 798.400 |
| Naive Bayes | 38.205 | 121 | R$ 1.910.250 | R$ 60.500 | R$ 1.970.750 |

## O achado central deste módulo

**Naive Bayes tem o maior recall (95,1%) de todos os modelos — e ainda assim é, disparado, o pior modelo pelo critério de custo.** Ele sinaliza quase tudo, incluindo 38.205 despesas legítimas, e cada uma dessas sinalizações tem um custo real (tempo de analista). Escolher um modelo só pela métrica de recall, sem olhar a tabela de custo, levaria à pior decisão possível aqui. **KNN vence em PR-AUC e em custo total simultaneamente** — mas isso não decide o modelo final do projeto ainda: os Módulos 7-8 trazem modelos mais fortes (XGBoost, ensembles) que serão comparados com esse baseline usando o mesmo critério de custo.

## Regressão Logística em odds ratio

`exp(coeficiente)` = quanto a chance de glosa multiplica quando aquela categoria está presente, tudo mais constante.

**Maior chance de glosa:**
- `TELEFONIA` → odds ratio **25,7x**
- `MANUTENÇÃO DE ESCRITÓRIO DE APOIO À ATIVIDADE PARLAMENTAR` → **12,7x**
- `FORNECIMENTO DE ALIMENTAÇÃO DO PARLAMENTAR` → **12,1x**

**Menor chance de glosa:**
- `PASSAGEM AÉREA - SIGEPA` → odds ratio **0,0023** (praticamente nunca tem glosa registrada dessa forma)
- `PASSAGEM AÉREA - RPA` → **0,062**
- `DIVULGAÇÃO DA ATIVIDADE PARLAMENTAR` → **0,131**

Isso é coerente com o que já sabíamos do Módulo 3: passagem aérea via SIGEPA já passa por um sistema centralizado com estornos/ajustes tratados de forma própria, raramente gerando glosa adicional. Categorias de menor valor unitário e mais fragmentadas (telefonia, manutenção de escritório) têm chance bem maior de ter parte reprovada.
