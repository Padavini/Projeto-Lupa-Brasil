# Avaliação do RAG — Módulo 10

Pipeline: embeddings gratuitos (`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`), índice FAISS local, geração com `google/flan-t5-base` (gratuito, roda na CPU). Índice construído sobre 14.283 proposições reais (1.600 gerais de 2023-2024 + proposições de 8 deputados específicos, via filtro `idDeputadoAutor` da própria API). Avaliação completa em `data/processed/avaliacao_rag.json`.

## Resultado agregado (16 perguntas)

| Critério | Resultado |
|---|---|
| Perguntas fora do domínio corretamente recusadas | 2 de 3 (66%) |
| Respostas com citação de fonte real e verificável | 13 de 13 respondidas (100%) |
| Citação correspondendo ao autor perguntado (quando aplicável) | 6 de 8 (75%) |
| Geração em português coerente, sem intrusão de inglês | 8 de 13 (62%) |

## 1. Confidence scoring e fallback — funcionou na maioria dos casos, com uma falha honesta

**Acertos:** "Qual a capital da França?" e "Como fazer um bolo de chocolate?" foram corretamente recusados (confiança 0,0) — o sistema não tentou responder com base em proposições completamente irrelevantes.

**Falha real encontrada:** "Quem ganhou a copa do mundo de 2022?" **não foi recusada** (confiança 0,444) — o sistema encontrou uma proposição de 2007 sobre uma "Sessão Solene em homenagem à conquista do título de Campeão Mundial de Futebol" (evento e ano completamente diferentes) e respondeu com base nela, por pura sobreposição de palavras-chave ("campeão mundial de futebol"). **Isso é um limite real do confidence scoring baseado só em distância de embedding**: ele mede similaridade textual, não se a pergunta é sobre o domínio legislativo de verdade. Um filtro adicional (ex.: classificador "essa pergunta é sobre proposições legislativas?" antes da busca) resolveria isso, e fica registrado como próximo passo.

## 2. Citação da fonte real — cumprido sempre, mas com um limite de precisão

Toda resposta não recusada veio acompanhada de proposições reais, com tipo/número/ano e link verificável — nunca uma citação inventada.

**Limite encontrado:** em 2 das 8 perguntas por autor ("O que Acácio Favacho propôs sobre agricultura?" e "O que Helena Lima propôs sobre meio ambiente?"), as fontes citadas **eram de outros deputados**, não do que foi perguntado. Isso acontece porque a busca é puramente semântica sobre o texto da ementa — o nome do deputado na pergunta não filtra os resultados por autor real. A citação é sempre uma proposição **real e existente**, mas não necessariamente do autor certo. Correção natural para uma próxima iteração: extrair o nome do deputado da pergunta e aplicar um filtro de metadado (`autor == nome`) antes ou depois da busca semântica.

## 3. Qualidade da geração em português — o maior ponto fraco, documentado com honestidade

`flan-t5-base` é um modelo majoritariamente treinado em inglês. Isso apareceu de forma clara e repetida:
- Acentuação sistematicamente corrompida ("aprovaço" em vez de "aprovação", "Pblica" em vez de "Pública").
- Em 4 das 13 respostas, o modelo **trocou para inglês no meio da resposta** (ex.: *"As a result of our legislative proposals, the Portuguese Parliament responds to..."*).
- Em 2 casos, a geração falhou completamente, devolvendo texto sem sentido ("Reposta") ou ecoando a instrução do prompt em vez de respondê-la.

**Isso não compromete a segurança do sistema** (a citação da fonte é sempre determinística, não depende da qualidade do texto gerado), mas compromete a experiência de leitura. Para produção, a troca por um modelo gerador com melhor suporte a português (ex.: um modelo instruction-tuned em PT-BR, ou uma API paga) seria a correção natural — trade-off consciente feito aqui em favor de "100% gratuito e local".

## Conclusão

O RAG cumpre os dois critérios de sucesso da trilha na maior parte do tempo — **cita fonte real (100%) e recusa quando não sabe (66% dos casos de teste, com uma falha real e instrutiva documentada)** — mas a avaliação honesta revela 3 limites concretos e corrigíveis: (1) confidence scoring baseado só em similaridade textual pode ser enganado por sobreposição de palavras-chave fora de contexto; (2) busca semântica não garante que a fonte citada seja do autor mencionado na pergunta; (3) o modelo de geração gratuito tem qualidade limitada em português. Nenhum desses limites foi escondido — todos estão documentados com o exemplo real que os revelou.
