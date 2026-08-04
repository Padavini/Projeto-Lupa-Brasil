# Quando deep learning fez sentido, e quando foi over-engineering — Módulo 9

## 1. MLP vs. LightGBM (dado tabular estruturado do projeto)

| Modelo | PR-AUC (teste real) | AUC-ROC (teste real) | Parâmetros |
|---|---|---|---|
| **LightGBM** (Módulo 7, tunado via Optuna) | **0,4121** | **0,8938** | — |
| MLP (PyTorch, 2 camadas escondidas) | 0,3493 | 0,8805 | 6.593 |

**Veredito: o LightGBM venceu, e isso é esperado, não uma falha do MLP.** Dado tabular com relativamente poucas features (69 após encoding) e relações não-lineares mas "simples" (ex.: uma categoria específica dominando o risco, como vimos no SHAP do Módulo 7) é exatamente o terreno em que árvores de decisão em ensemble tendem a vencer redes neurais — elas lidam bem com splits categóricos, não precisam de tanto dado pra generalizar, e não sofrem com a "maldição" de otimizar milhares de pesos quando a estrutura do problema é mais simples que isso. O MLP não é ruim (AUC-ROC ainda razoável, 0,88), só não tem vantagem aqui.

## 2. CNN (transfer learning) e Autoencoder — laboratório genérico (Fashion MNIST)

- **Transfer learning (ResNet18 pré-treinado, só a última camada treinada):** 77,55% de acurácia em 3 épocas, usando um subconjunto de 8.000 imagens. Isso ilustra bem a vantagem central do transfer learning: reaproveitar características visuais já aprendidas (bordas, texturas, formas) de uma rede treinada em milhões de imagens, sem precisar re-treinar tudo do zero.
- **Autoencoder:** erro de reconstrução (MSE) caiu de 0,093 para 0,020 em 10 épocas — reconstrução visualmente reconhecível, mas com perda de detalhe fino (esperado, comprimindo 784 pixels em 32 números).

Esse laboratório não usa dado do projeto — é prática isolada de conceito, como a própria trilha propõe, antes de aplicar deep learning ao dado real (feito na LSTM a seguir).

## 3. LSTM — prevendo o gasto do próximo mês (dado real do projeto)

| Abordagem | MAE (R$) |
|---|---|
| Baseline ingênuo (repete o último mês) | R$ 16.778,56 |
| LSTM (após corrigir treino para mini-batch, 50 épocas) | R$ 17.186,58 |

**Veredito: a LSTM não superou o baseline ingênuo — ficou apenas 2,4% pior.** Esse é um resultado honesto e revelador: o gasto mensal de um deputado tem forte "persistência" (o mês seguinte tende a se parecer com o atual), o que torna o baseline trivial **surpreendentemente difícil de bater**. Isso não significa que a LSTM esteja quebrada — o treinamento revelou um erro real no processo (a primeira tentativa usava apenas 20 atualizações de gradiente no total, sem mini-batch, e teve desempenho muito pior; corrigido, a LSTM chegou perto do baseline). Mesmo corrigida, o ganho de complexidade não se traduziu em ganho de precisão mensurável.

## Item bônus não feito

O exercício bônus da trilha (classificador de texto com Hugging Face Transformers sobre descrição de despesa/proposição) foi deliberadamente deixado de fora nesta rodada — é explicitamente opcional na trilha, e o tempo foi priorizado nos 3 itens obrigatórios (MLP, CNN/Autoencoder, LSTM), consistente com a própria orientação da trilha de que deep learning pode ter menos profundidade sem comprometer o restante do projeto.

## Conclusão geral: onde deep learning fez sentido, e onde foi complexidade desnecessária

- **Fez sentido:** no laboratório de imagem (CNN/Autoencoder), onde a estrutura espacial dos pixels é exatamente o tipo de padrão que redes neurais (convolucionais) capturam melhor que qualquer método clássico.
- **Foi over-engineering, nesse estágio do projeto:** tanto o MLP quanto a LSTM, aplicados ao dado tabular/temporal do Projeto Lupa, não superaram alternativas mais simples e mais baratas de treinar/manter (LightGBM e um baseline de uma linha, respectivamente). Isso não é um argumento contra deep learning em geral — é um argumento a favor de **sempre comparar contra um baseline simples antes de assumir que o modelo mais sofisticado é o melhor**. Para os próximos módulos do projeto (RAG, engenharia, deploy), a base de decisão de modelo pro `houve_glosa` continua sendo o LightGBM do Módulo 7.
