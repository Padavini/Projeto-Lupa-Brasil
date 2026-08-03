# Calibração de threshold e probabilidade — Módulo 7

Modelo: LightGBM final (PR-AUC 0,4121, AUC-ROC 0,8938 no teste real). Custos assumidos: R$ 50 por falso positivo, R$ 500 por falso negativo (mesmo critério do Módulo 6).

## Threshold ótimo pela curva PR, não o padrão 0,5

| Threshold | Custo total | Precision | Recall |
|---|---|---|---|
| 0,5 (padrão) | R$ 676.950,00 | — | — |
| **0,673 (ótimo pelo custo)** | **R$ 598.950,00** | 0,268 | 0,713 |

**Economia: R$ 78.000,00** (11,5% de redução de custo) só por escolher o threshold que minimiza custo real, em vez do 0,5 que o `predict()` usa por padrão sem nenhuma justificativa de negócio.

Importante: o threshold ótimo (0,673) é **mais alto** que 0,5 — o modelo, com esse custo assumido (FN 10x mais caro que FP), na verdade deveria ser ligeiramente mais conservador em sinalizar do que se pensaria à primeira vista. Isso mostra que a intuição "quanto menor o threshold, mais barato porque pega mais glosa" nem sempre vale — depende de como o modelo distribui os scores nos dois lados desse ponto.

## Calibração de probabilidade (Brier score)

Ranquear bem (boa PR-AUC) não significa que a probabilidade em si está correta — um modelo pode dizer "90% de chance" quando a chance real de despesas com aquele score é mais perto de 60%. Calibramos com `CalibratedClassifierCV` (método isotônico), ajustado **só no conjunto de validação** (nunca no teste, mesma disciplina anti-leakage do Módulo 5).

| | Brier score |
|---|---|
| Antes da calibração | 0,1131 |
| **Depois (isotônica)** | **0,0330** |
| Melhora | **70,8%** |

Brier score menor = probabilidades mais próximas da frequência real observada. A melhora de 70,8% é grande, indicando que o modelo cru (antes de calibrar) estava com probabilidades bem distorcidas — provavelmente porque `is_unbalance=True` no LightGBM reponderou as classes durante o treino, o que melhora a separação (ranking) mas distorce a escala das probabilidades. A calibração corrige essa escala sem alterar o ranking (PR-AUC/AUC-ROC continuam os mesmos).

## Recomendação final

Para uso em produção (ex.: threshold usado no painel público pra decidir o que aparece como "sinalizado"), usar o modelo **calibrado** com o **threshold de 0,673** sobre a probabilidade calibrada — não o padrão 0,5 do `.predict()`, e não a probabilidade crua do modelo.
