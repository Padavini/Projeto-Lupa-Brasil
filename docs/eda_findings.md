# Achados da EDA — Módulo 3

Análise exploratória sobre 640.518 despesas de 512 deputados (eleição de 2022 em diante, R$ 801,7 milhões no total). Notebook completo em `notebooks/01_eda.ipynb`.

## 1. O ranking de gasto individual é dominado por um confundidor geográfico

Os 20 deputados que mais gastaram vêm quase todos de UFs distantes de Brasília ou de grande extensão territorial (AM, RR, RO, AC, RS, MS). Isso não indica, por si só, comportamento irregular — é o custo de passagem aérea/deslocamento de quem representa uma região longe da capital. Qualquer ranking exibido publicamente precisa vir acompanhado dessa explicação, sob risco de sugerir uma leitura errada (ver `docs/principios_responsabilidade.md`). Esse confundidor será formalmente testado com estatística no Módulo 4.

## 2. Gasto total por partido reflete tamanho de bancada, não "gastança"

PL (R$ 156M) e PT (R$ 108M) lideram em valor absoluto — mas isso só reflete que são as maiores bancadas da Casa. Ao calcular o **gasto médio por deputado**, a ordem muda bastante (ver notebook, seção de visualizações). Comparar partidos exige sempre normalizar pelo número de deputados; comparar só o total absoluto é enganoso.

## 3. Companhias aéreas concentram gasto, mas o dado sobre elas está fragmentado

As 4 primeiras posições do ranking de fornecedores são companhias aéreas. O problema: a mesma empresa aparece sob nomes diferentes ("AZUL" e "Azul Linhas Aéreas", "GOL" e "Gol Linhas Aéreas", "TAM" e "LATAM Airlines Brasil" tratadas como entidades distintas), porque **19,4% das despesas** — todas da categoria "PASSAGEM AÉREA - SIGEPA" — não têm CNPJ preenchido, o campo que normalmente permitiria unificar variações de nome. Esse é um problema de qualidade de dado real e sistemático, ligado ao sistema de emissão de passagens da própria Câmara (SIGEPA), não um erro aleatório. Fica registrado para tratamento no próximo passo do Módulo 3 (normalização de nome de fornecedor).

## 4. Valores negativos existem, e têm explicação mundana — não são erro nem irregularidade

10.142 despesas (todas de "PASSAGEM AÉREA - SIGEPA") têm valor negativo. Em todas elas, `valor_liquido` é idêntico a `valor_documento` e `valor_glosa` é zero — um padrão consistente com estornos/ajustes de tarifa aérea (cancelamento, diferença de valor devolvida), não uma anomalia de lançamento. Investigar antes de rotular é o processo correto diante de qualquer valor que pareça estranho à primeira vista.

## 5. A regra clássica de outlier (1,5×IQR) não é adequada para esse dado, e isso é um achado em si

Aplicando a regra padrão de outlier por IQR, **10,32% das despesas** seriam sinalizadas como atípicas — um volume alto demais para ser útil como sinal de "atenção". A causa é estrutural: o gasto de despesa é naturalmente assimétrico à direita (muitas compras pequenas, poucas grandes), então a cauda direita da distribuição normal já ultrapassa o limite ingênuo do IQR. Esse achado antecipa a necessidade dos métodos mais sofisticados de detecção de anomalia (Isolation Forest, LOF) previstos para o Módulo 8 — a abordagem estatística simples não segmenta bem aqui.

## Decisão de limpeza aplicada

Normalizamos manualmente as 4 maiores companhias aéreas (TAM/LATAM Airlines Brasil → `LATAM`; AZUL/Azul Linhas Aéreas → `Azul`; GOL/Gol Linhas Aéreas → `Gol`), com base em conhecimento de domínio — já que o CNPJ, que resolveria isso automaticamente, está ausente nessas despesas. TAM e LATAM foram tratadas como a mesma marca comercial (rebranding de 2016). Resultado: `LATAM` sozinha soma R$ 103,7 milhões, consolidando o que antes aparecia espalhado em nomes diferentes. Essa é uma normalização manual, específica dos 3 maiores casos conhecidos — não resolve fornecedores menores com o mesmo problema, o que fica em aberto pra uma abordagem mais geral (ex.: fuzzy matching) se necessário mais adiante.

## Também notado, sem aprofundar ainda

- Evolução mensal mostra padrão sazonal claro: pico de gasto em novembro/dezembro (fim de ano legislativo) e queda em janeiro (recesso).
