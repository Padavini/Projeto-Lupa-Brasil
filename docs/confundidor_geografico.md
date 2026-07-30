# Confundidor geográfico no gasto parlamentar — Módulo 4

## A pergunta

O ranking de gasto (Módulo 2/3) mostrava deputados de UFs distantes/grandes no topo. Será que isso é sobre o **partido** desses deputados, ou sobre **de onde eles vêm**? Testamos formalmente com `statsmodels`, usando a distância rodoviária aproximada de cada capital estadual até Brasília como proxy do custo geográfico de mandato.

## Os 3 modelos testados

| Modelo | R² | Achado |
|---|---|---|
| `gasto_total ~ distancia_bsb_km` | 0,027 | Coeficiente **+R$ 109,43** por km (p < 0,001) — significativo, mas explica pouco do gasto total sozinho |
| `gasto_total ~ C(partido)` | 0,057 | F-test **p = 0,085** — não significativo a 5% |
| `gasto_total ~ C(partido) + distancia_bsb_km` | 0,080 | Distância continua significativa (p < 0,001) mesmo controlando por partido |

**Refinamento:** ao testar a distância especificamente contra o **gasto com passagem aérea** (o canal causal mais direto), o coeficiente permanece positivo e significativo: `gasto_passagem ~ distancia_bsb_km` → coeficiente **+R$ 52,53 por km** (p < 0,001).

## Conclusão

A distância até Brasília é uma variável **estatisticamente significativa** para explicar o gasto de um deputado, tanto no total quanto em passagem aérea especificamente — e continua significativa mesmo depois de controlar pelo partido. Já o partido, sozinho, **não atinge significância estatística a 5%** (p = 0,085) para explicar diferenças de gasto total.

Isso reforça, com número e não só intuição, o motivo pelo qual o `data_product_brief.md` e os `principios_responsabilidade.md` do projeto proíbem qualquer ranking ou sinalização pública sem contexto: uma leitura ingênua do ranking ("esse deputado gasta muito") pode facilmente confundir geografia com comportamento. O R² modesto (não é uma relação determinística — outros fatores como frequência de viagem também importam) não invalida o achado: a significância estatística mostra que o efeito é real, mesmo que não seja o único fator.

## Limitação assumida

A tabela de distâncias é uma aproximação rodoviária de capital a capital, feita manualmente com base em conhecimento geográfico geral — não é um dado oficial da API. Suficiente para demonstrar o confundidor com números, mas não deveria ser usada como componente de precisão num modelo de produção sem validação por fonte oficial (ex.: IBGE).
