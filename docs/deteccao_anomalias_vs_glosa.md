# Detecção de anomalia "às cegas" vs. rótulo real — Módulo 8

Pergunta da trilha: **é possível detectar um padrão irregular sem nenhum histórico rotulado?** Testamos Isolation Forest e Local Outlier Factor (LOF) sobre 80.000 despesas amostradas, usando só `valor_documento`, `categoria`, `partido` e `uf` — **sem olhar `houve_glosa`** — e revelamos o rótulo real só no final, pra medir o resultado.

## Configuração

Ambos os métodos configurados com `contamination=0.05` (uma suposição a priori de que ~5% do dado seria atípico, escolhida sem consultar a proporção real de glosa — que já sabíamos, do Módulo 5, ser 4,79%. A coincidência do valor escolhido é intencional: um analista sem rótulo ainda pode ter uma noção geral de "quanto deveria ser raro").

## Resultado, com o rótulo revelado

| Método | Precision | Recall | Despesas sinalizadas |
|---|---|---|---|
| **Isolation Forest** | 0,099 | 0,102 | 4.000 (5,00%) |
| **LOF** | 0,049 | 0,050 | 4.000 (5,00%) |

Proporção real de glosa na amostra: 4,87%.

**Concordância entre os dois métodos:** apenas 186 despesas (de 4.000 cada) foram sinalizadas por ambos — os dois métodos, olhando o mesmo dado, "discordam" na maior parte do que consideram anômalo.

## Interpretação honesta

- **Isolation Forest** teve desempenho **modesto, mas real**: precision (9,9%) e recall (10,2%) ficaram cerca do **dobro** do que se esperaria de uma sinalização aleatória (que daria ~4,9%, a própria taxa base de glosa). Existe algum sinal, mas fraco.
- **LOF** teve desempenho **equivalente a chute aleatório** — precision e recall praticamente idênticos à taxa base (4,87%). Nesse recorte de features, LOF não capturou nenhum sinal útil sobre glosa.
- **Comparando com o Módulo 7:** o modelo supervisionado (LightGBM, PR-AUC 0,41) teve desempenho muito superior a qualquer um dos métodos cegos. Isso faz sentido: `houve_glosa` é uma decisão administrativa específica da Câmara, não necessariamente correlacionada com "ser estatisticamente incomum" no espaço geral de features — uma despesa pode ser rara sem ter glosa, e comum e ainda assim ter glosa. Aprendizado supervisionado consegue capturar esse padrão específico (ex.: a importância de "Passagem Aérea SIGEPA" no SHAP do Módulo 7); detecção de anomalia não tem acesso a esse sinal direcionado.

## Resposta à pergunta da trilha

Sim, é possível detectar *algum* padrão irregular sem rótulo (Isolation Forest supera o acaso) — mas o resultado é fraco e não deveria, sozinho, embasar qualquer sinalização pública. Isso reforça, com número, por que o projeto usa aprendizado supervisionado (Módulo 6-7) como abordagem principal para `houve_glosa`, e trata clustering/anomalia como ferramenta complementar de exploração (perfis de gasto), não como mecanismo de sinalização de despesa individual.
