# Princípios de Responsabilidade — Projeto Lupa

O dado usado neste projeto é público e oficial (API de Dados Abertos da Câmara dos Deputados), mas o produto final nomeia pessoas reais. Isso muda o padrão de cuidado em relação a um projeto de dados comum. As regras abaixo são editoriais e técnicas, e valem para todo o time (hoje, só eu) em qualquer módulo do projeto.

## Regra 1 — Vocabulário

Nunca usar **"fraude"** ou **"corrupção"** em código, commit, docstring, nome de coluna, variável, log ou UI, sem apuração jornalística ou decisão judicial que sustente o termo — o que este projeto não tem e não produz.

O termo correto é:
- **"gasto atípico"** — quando um valor foge do padrão estatístico do grupo de comparação (categoria, partido, UF).
- **"despesa sinalizada para checagem"** — quando um modelo aponta uma despesa como candidata a revisão humana.

Não existe rótulo de fraude no dado da API. O único sinal objetivo disponível é `valorGlosa` — quando a própria Câmara reprova parte de uma despesa. O target de ML do projeto (`houve_glosa = valorGlosa > 0`) mede glosa administrativa, não fraude. Essa distinção deve ser explícita em qualquer lugar que o modelo apareça (notebook, docs, UI).

## Regra 2 — Toda sinalização vem com explicação

Nenhum score de risco, cluster ou anomalia é exibido publicamente sem a explicação correspondente (SHAP, para modelos supervisionados; descrição do perfil/cluster, para não supervisionados).

Na prática:
- Não existe endpoint ou view que retorne só o score numérico para consumo público.
- A explicação acompanha o número no mesmo payload/tela — não como link separado ou "saiba mais" opcional.
- A explicação é escrita em linguagem acessível (o teste é: um jornalista sem background técnico entende sem precisar perguntar).

## Regra 3 — Disclaimer permanente e visível

O painel público mantém, em todas as páginas que exibem dado de deputado, um disclaimer visível com:
1. Fonte oficial dos dados (API de Dados Abertos da Câmara dos Deputados) e link.
2. Data da última atualização dos dados.
3. O que "sinalizado" significa e — igualmente importante — **o que não significa**: não é acusação, não é veredicto, é um padrão estatístico que pode ter explicação legítima (ex.: despesa de deputado de UF distante custa mais em passagem).

## Processo de revisão

Antes de mergear qualquer feature que afete o que é exibido publicamente (nova visualização, novo score, nova coluna em tabela pública), revisar contra as três regras acima. Se a feature violar qualquer uma, ela não vai ao ar até ser corrigida — não existe exceção "só para teste" em produção.

## Por que isso é modelado antes de qualquer dado ir ao ar

Formalizar essas regras no módulo 1 (antes de qualquer linha de ingestão) é intencional: é mais fácil desenhar schema, nomes de coluna e contrato de API certos desde o início do que corrigir depois que "score_fraude" já vazou para dez lugares do código.
