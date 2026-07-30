# Jornada do Projeto Lupa — por que cada módulo importa

## Módulos já feitos

### Módulo 1 — Data Product Brief e princípios de responsabilidade

Antes de qualquer linha de código, definimos **para quem** o painel serve e **o que ele nunca pode fazer** (nunca sinalizar sem explicação, nunca usar "fraude"). Isso importa porque é o que separa um projeto de portfólio genérico de um produto de dados de verdade — em entrevista, "como você define escopo de um produto que expõe dado de pessoas reais?" é pergunta que só quem passou por esse exercício responde bem, sem enrolação.

### Módulo 2 — Ingestão, Postgres, star schema, window functions

Aqui aprendemos a **trazer dado real de forma confiável** (idempotente, sem duplicar) e a **modelar** ele de um jeito que qualquer analista consiga consultar sem reprocessar tudo do zero. O star schema (fato + dimensões) é o padrão que praticamente toda empresa com um data warehouse usa — sem isso, você tem dado, mas não tem *infraestrutura* pra analisar dado. Window functions (`RANK`, `LAG`, média móvel) são o que separa "sei fazer SELECT" de "sei responder pergunta de negócio com SQL" — extremamente comum em entrevista técnica.

### Módulo 3 — EDA em pandas

Esse módulo importa porque é onde você **desconfia do próprio dado antes de confiar nele**. Descobrimos duas coisas que pareciam bugs (CNPJ ausente, valores negativos) e, investigando em vez de assumir, viraram explicações mundanas (SIGEPA, estornos de passagem). Essa disciplina — nunca rotular um dado estranho sem investigar — é exatamente o que evita que um projeto de dados sobre pessoas reais vire uma acusação injusta.

### Módulo 4 — Estatística e Inferência

Aqui trocamos **intuição por número**. "Parece que deputado de estado distante gasta mais" virou uma hipótese testada com regressão, com p-valor, provando que geografia é estatisticamente significativa e partido sozinho não é. Isso é o que dá **credibilidade** a qualquer afirmação que o painel público fizer — e o teste A/B ensinou algo raro de aprender só na prática: um resultado "não significativo" não prova que não há efeito, pode ser falta de poder estatístico. Isso é o tipo de nuance que diferencia quem manja de estatística de quem só roda testes sem entender o que eles significam.

### Módulo 5 — Target e pré-processamento de ML

Esse é o módulo-charneira: tudo antes dele foi "entender o dado", tudo depois vai ser "usar o dado pra prever algo". Ele importa porque resolveu, de forma testada e comprovada, os dois erros mais comuns e mais graves em ML aplicado a dado real: **vazamento temporal** (treinar com informação do futuro) e **vazamento estatístico** (ajustar o scaler vendo o teste). Um modelo construído sem esse cuidado pode parecer ótimo no notebook e falhar completamente em produção — é o tipo de erro que profissionais sênior sabem procurar primeiro ao revisar um pipeline de ML.

## O que vem a seguir, e por que vai importar

### Módulo 6 — Modelos Supervisionados (próximo)

Aqui treinamos os primeiros classificadores de verdade (Regressão Logística, KNN, Naive Bayes, SVM) prevendo `houve_glosa`. A importância real não é o modelo em si — é a **tabela de custo** (falso positivo vs falso negativo) e o porquê de usar PR-AUC em vez de acurácia. Isso ensina a conectar métrica técnica a decisão de negócio: sinalizar uma despesa legítima por engano tem um custo diferente de deixar passar uma atípica, e a escolha do modelo deveria refletir isso, não só "qual número de acurácia é maior".

### Módulo 7 — Ensembles, MLflow, SHAP

Aqui entram os modelos mais fortes (XGBoost, LightGBM, CatBoost) e, mais importante pro produto, o **SHAP** — a explicabilidade que o `principios_responsabilidade.md` exige antes de qualquer sinalização ir ao ar. MLflow importa porque rastreia experimentos: sem isso, depois de 15 tentativas de modelo você não lembra qual configuração deu qual resultado. Isso é infraestrutura de ML profissional, não luxo.

### Módulo 8 — Não supervisionado e anomalias

Aqui detectamos padrão **sem usar o rótulo de glosa**, e só depois comparamos com o rótulo real. Isso importa porque, na vida real, você frequentemente não tem rótulo nenhum — saber clusterizar e achar outlier "às cegas" é uma habilidade que aparece direto em entrevista de dados sênior, e reforça de novo o cuidado de não confundir "gasto fora do padrão" com "gasto irregular".

### Módulo 9 — Redes Neurais

Menos sobre "usar deep learning porque é moderno" e mais sobre **saber quando não vale a pena**. Comparar MLP com XGBoost honestamente, e escrever quando deep learning fez sentido e quando foi over-engineering, é uma resposta de entrevista rara — a maioria só sabe "aplicar", poucos sabem "julgar se deveria".

### Módulo 10 — RAG sobre proposições

Esse é o módulo mais alinhado com o que o mercado pede agora. Construir um assistente que **cita a fonte real** e **admite quando não sabe** é a diferença entre um chatbot de brinquedo e um sistema confiável — especialmente importante aqui, onde inventar uma proposição que um deputado nunca fez seria um dano real.

### Módulo 11 — Engenharia de Software

Até aqui, tudo é notebook e script solto. Esse módulo transforma isso num **pacote instalável, testado, com CI** — é o que faz um recrutador técnico olhar o repositório e reconhecer "essa pessoa sabe entregar software", não só "essa pessoa sabe fazer análise".

### Módulo 12 — MLOps

Aqui o projeto vira um serviço de verdade: containerizado, com monitoramento de drift. Isso importa porque modelo de ML não é "treinar e esquecer" — dado muda (nova legislatura, nova regra de teto), e um sistema profissional precisa **perceber** quando está ficando desatualizado, não continuar servindo previsão errada silenciosamente.

### Entregável final — o painel público

É onde tudo isso vira algo que **uma pessoa de fora pode usar e confiar**, com o disclaimer e a explicação sempre visíveis — o teste real de que o projeto cumpriu a promessa escrita no Módulo 1, lá no início.
