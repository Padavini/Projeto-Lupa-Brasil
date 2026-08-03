# Relatório SHAP — Módulo 7

Modelo: LightGBM (vencedor do tuning via Optuna, PR-AUC 0,4121 no teste real — ver `docs/mlflow_experimentos.md`). Explicações geradas com `shap.TreeExplainer`.

## Explicação global — o que mais pesa na previsão, em média

| Feature | Importância (SHAP média absoluta) |
|---|---|
| Categoria = Passagem Aérea (SIGEPA) | 2,86 |
| Categoria = Combustíveis e Lubrificantes | 0,77 |
| Valor da despesa | 0,71 |
| Categoria = Divulgação da Atividade Parlamentar | 0,40 |
| Categoria = Hospedagem (fora do DF) | 0,15 |
| Partido = PL | 0,07 |
| UF = SP | 0,06 |

**Em linguagem acessível:** de longe, o fator mais importante para o modelo é se a despesa é ou não de passagem aérea via SIGEPA — como vimos desde o Módulo 3, esse sistema centralizado praticamente nunca gera glosa, então essa categoria "puxa" fortemente a previsão pra baixo quando presente, e sua ausência "libera" a previsão pra subir. Combustíveis e o valor da despesa em si vêm em seguida — despesas maiores e de certas categorias específicas concentram a maior parte do sinal de risco que o modelo aprendeu.

## Explicações locais — 3 despesas reais

### 1. Acerto — glosa real detectada corretamente
- Categoria: Locação ou fretamento de veículos automotores | Partido: PL | UF: PR
- Valor: R$ 1.111,85 | Score do modelo: 0,992 | Glosa real: **sim**
- **Por quê o modelo sinalizou:** essa despesa não é do tipo "passagem aérea" (que normalmente reduz bastante o risco) e tem valor relativamente alto para a categoria de locação de veículo — dois fatores que, juntos, empurraram a previsão fortemente para "risco de glosa". O modelo acertou: essa despesa teve glosa de verdade.

### 2. Falso positivo — sinalizado sem glosa real
- Categoria: Locação ou fretamento de veículos automotores | Partido: Republicanos | UF: PB
- Valor: R$ 17.500,00 | Score do modelo: 0,985 | Glosa real: **não**
- **Por quê o modelo errou:** o valor alto (R$ 17.500) e a categoria (fora de passagem aérea) fizeram o modelo prever risco alto — mas essa despesa específica não teve glosa. É um exemplo real do custo de falso positivo discutido no Módulo 6: um valor grande numa categoria de risco não é garantia de irregularidade, pode ser uma locação legítima e cara. Isso reforça por que a sinalização nunca deve ser tratada como acusação — é um indício estatístico, sujeito a erro, que precisa de checagem humana.

### 3. Acerto — sem glosa, alta confiança
- Categoria: Passagem Aérea (SIGEPA) | Partido: Republicanos | UF: AC
- Valor: R$ -31,95 (estorno) | Score do modelo: 0,000 | Glosa real: **não**
- **Por quê o modelo acertou com tanta confiança:** exatamente o padrão contrário ao caso 1 — é uma despesa de passagem aérea via SIGEPA (a categoria que mais reduz o risco no modelo) e, sendo um valor negativo (estorno, como vimos no Módulo 3), o modelo aprendeu que esse padrão praticamente nunca acompanha glosa.

## Achado de transparência sobre o próprio método

Repare no caso 2: mesmo a despesa não sendo de "Passagem Aérea", essa categoria aparece entre os fatores que mais influenciaram a previsão. Isso acontece porque, com features categóricas transformadas em colunas binárias (one-hot encoding), o SHAP também mede o efeito de uma categoria **estar ausente** — já que "não ser passagem aérea" já é, por si, uma informação que eleva o risco de base (essa categoria costuma isentar quase todo mundo). Vale ter isso em mente ao explicar o modelo pra um público não técnico: a ausência de uma categoria "protetora" também conta como sinal.
