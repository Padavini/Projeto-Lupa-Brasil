# Desenho de teste A/B — novo teto de reembolso (Combustíveis e Lubrificantes)

## Cenário

A Câmara propõe reduzir o teto de reembolso da categoria "Combustíveis e Lubrificantes", esperando reduzir o gasto médio mensal por deputado em pelo menos um certo percentual (o MDE — Minimum Detectable Effect). Grupo controle = teto atual; grupo tratamento = novo teto.

## Baseline real (calculado a partir do dado do projeto)

- Gasto médio mensal por deputado: **R$ 3.355,17**
- Desvio padrão: **R$ 2.125,34**
- (baseado no gasto total de cada deputado na categoria, dividido por ~43 meses de mandato)

## Sensibilidade do tamanho de amostra ao MDE

| MDE | Efeito absoluto | Effect size (Cohen's d) | n necessário por grupo |
|---|---|---|---|
| 5% | R$ 167,76 | 0,079 | **2.521** |
| 10% | R$ 335,52 | 0,158 | **631** |
| 15% | R$ 503,27 | 0,237 | **281** |
| 20% | R$ 671,03 | 0,316 | **158** |

(`alpha=0.05`, `power=0.80`, teste bicaudal)

## Achado crítico: o universo de 512 deputados limita o que é detectável

Com **512 deputados no total**, um MDE de 5% ou 10% exigiria mais deputados por grupo do que o universo inteiro comporta (631-2.521 necessários vs. 512 disponíveis). Isso significa que, dado o tamanho fixo da Câmara, **mudanças pequenas no gasto médio (5-10%) não são estatisticamente detectáveis com confiança** num teste A/B tradicional dividindo os próprios deputados em grupos. Só efeitos de 15-20% ou maiores são viáveis de detectar dessa forma.

## Simulação executada (MDE 20%, n=158 por grupo)

- Média controle (teto atual): R$ 3.255,41
- Média tratamento (teto novo): R$ 2.938,46
- Redução observada: 9,7% (menor que os 20% assumidos na simulação)
- Estatística t: 1,441 — **p-valor: 0,151** (não significativo a 5%)

## Por que o resultado não deu significativo, e o que isso ensina

O cálculo de amostra foi feito para **80% de poder estatístico** — não 100%. Isso significa, por definição, que existe **20% de chance de não detectar um efeito real** mesmo quando ele de fato existe, simplesmente por variação aleatória da amostra. Essa simulação específica caiu nesse cenário: a diferença observada (9,7%) ficou abaixo do efeito assumido (20%) só por sorte da amostragem, e o teste não atingiu significância.

Isso não invalida o cálculo de amostra — pelo contrário, é uma demonstração real de por que poder estatístico nunca é 100% na prática, e por que um único resultado "não significativo" não prova que "não há efeito": pode ser um falso negativo dentro da margem de erro esperada e assumida no desenho do teste.

## Conclusão em linguagem de gestão pública

Se a Câmara quiser testar formalmente um novo teto de reembolso de combustível, o tamanho da amostra necessário depende diretamente de quão grande é a redução que se espera detectar: reduções pequenas (5-10%) exigiriam mais deputados do que a Casa tem hoje, tornando esse teste inviável nesse desenho. Reduções maiores (15-20%) são estatisticamente viáveis com o quadro atual de deputados. Além disso, mesmo um teste corretamente desenhado tem uma chance residual (aqui, 20%) de não confirmar um efeito real que de fato existe — um resultado "sem diferença significativa" não é o mesmo que "a mudança não funcionou", pode ser falta de poder estatístico na amostra observada.
