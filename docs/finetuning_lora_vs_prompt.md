# Fine-tuning com PEFT/LoRA vs. Prompt Engineering — Módulo 10

## Tarefa

Classificar o tema de uma proposição legislativa a partir da ementa, em 5 categorias (saúde, educação, segurança, meio ambiente, outro) — rótulos construídos por palavra-chave (heurística, não é rótulo oficial da API; suficiente para comparar as duas técnicas, não para produção).

## Resultado

| Abordagem | Acurácia no teste (100 exemplos) | Parâmetros treinados |
|---|---|---|
| **Prompt engineering puro** (zero-shot, `flan-t5-base`) | **27,00%** | 0 |
| **Fine-tuning com LoRA** (`neuralmind/bert-base-portuguese-cased` + PEFT) | **86,00%** | 298.757 de 109.225.738 (0,27%) |

## Interpretação honesta

**27% está muito perto do chute aleatório** (20% seria o esperado ao sortear entre 5 classes) — na prática, o `flan-t5-base` mal conseguiu usar a instrução do prompt pra classificar corretamente em português. Isso confirma, de outro ângulo, o mesmo limite já visto no `docs/rag_eval.md`: esse modelo é fraco em português.

**86% de acurácia treinando só 0,27% dos parâmetros** é a demonstração prática do valor do LoRA: em vez de re-treinar os 109 milhões de parâmetros do BERTimbau (caro, lento, arriscado de "esquecer" o que o modelo já sabia), o LoRA injeta pequenas matrizes treináveis em cima do modelo congelado — resultado: treino rápido até em CPU (4 épocas, poucos minutos), e uma melhora de mais de 3x sobre o zero-shot.

## Conclusão

Para tarefas específicas e bem definidas (como classificar tema de texto), **fine-tuning barato (LoRA) supera largamente prompt engineering com um modelo genérico fraco no idioma**. Isso não significa que prompt engineering nunca funcione — com um modelo maior ou mais adequado ao português (ou com poucos exemplos no prompt, few-shot), o resultado zero-shot provavelmente melhoraria. Mas, dado o modelo gratuito disponível neste projeto, a lição prática é clara: quando existe dado rotulado (ainda que por heurística) e a tarefa é restrita, vale mais a pena investir num fine-tuning leve do que depender só da qualidade do prompt.
