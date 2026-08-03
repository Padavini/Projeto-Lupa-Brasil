# Experimentos MLflow — Módulo 7

Tracking configurado com backend SQLite local (`sqlite:///mlflow.db`) — o backend de arquivo puro (`./mlruns`) está em modo de manutenção nas versões recentes do MLflow e não recebe mais atualizações.

## Resumo

- **Experimento:** `lupa-houve-glosa`
- **Total de runs registrados:** 66 (bem acima do mínimo de 15 pedido pela trilha — cada rodada de tuning do Optuna gera 1 run por tentativa, mais os runs de agregação por modelo e o run final)
- **Modelos tunados via Optuna:** XGBoost, LightGBM, CatBoost (6 tentativas cada)
- **Métrica de tuning:** PR-AUC, calculada num conjunto de validação **dentro do treino** (nunca no teste), evitando overfitting na escolha de hiperparâmetro

## Melhor resultado por modelo (validação)

| Modelo | Melhor PR-AUC (validação) |
|---|---|
| **LightGBM** | **0,4669** |
| CatBoost | 0,4544 |
| XGBoost | 0,4444 |

## Modelo final promovido

- **Modelo:** LightGBM, com os melhores hiperparâmetros encontrados pelo Optuna, retreinado no treino completo
- **PR-AUC no teste real (nunca visto durante o tuning):** 0,4121
- **AUC-ROC no teste real:** 0,8938
- **Registrado no MLflow Model Registry como:** `lupa-houve-glosa-lightgbm`, versão 1

Essa performance é uma melhora clara sobre o baseline do Módulo 6 (KNN, PR-AUC 0,321) — os ensembles com tuning capturam padrões mais sutis nas mesmas features.

## Decisão técnica: pandas fixado em <3

Ao instalar o MLflow, o `pandas 3.0.5` (instalado automaticamente antes) se mostrou incompatível — MLflow ainda não suporta pandas 3.x. Fixamos `pandas>=2.2,<3` no `pyproject.toml`. Todos os notebooks anteriores foram re-executados e continuam passando (incluindo os testes automatizados em `tests/`), confirmando que o downgrade não quebrou nada do projeto.
