"""Pipeline de RAG sobre proposições legislativas - Módulo 10.

100% gratuito e local: embeddings via sentence-transformers, índice vetorial
via FAISS, geração via um modelo pequeno do Hugging Face rodando na CPU.
Nunca responde sem citar a fonte real; recusa quando a confiança é baixa.
"""

import os
from dataclasses import dataclass

import requests
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

BASE_URL = "https://dadosabertos.camara.leg.br/api/v2"
CAMINHO_INDICE = "../data/processed/faiss_proposicoes"
MODELO_EMBEDDING = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
MODELO_GERACAO = "google/flan-t5-base"
# calibrado empiricamente: perguntas relevantes tiveram distância L2 ~10-13,
# perguntas fora do domínio (ex.: "qual a capital da França") ficaram em ~28-33
DISTANCIA_MAXIMA_RELEVANTE = 25.0
LIMIAR_CONFIANCA = 0.30


@dataclass
class RespostaRAG:
    resposta: str
    confianca: float
    fontes: list[dict]
    recusou: bool


def _fetch_com_retry(url: str, params: dict | None = None, tentativas: int = 3) -> dict:
    for tentativa in range(1, tentativas + 1):
        try:
            r = requests.get(url, params=params, timeout=15)
            r.raise_for_status()
            return r.json()
        except requests.exceptions.RequestException:
            if tentativa == tentativas:
                raise


def fetch_proposicoes_gerais(anos: list[int], max_paginas_por_ano: int = 15) -> list[dict]:
    """Busca proposições recentes, por ano, sem filtro de autor - base geral por tema."""
    proposicoes = []
    for ano in anos:
        url = f"{BASE_URL}/proposicoes"
        params = {"ano": ano, "itens": 100, "ordem": "DESC", "ordenarPor": "id"}
        paginas_lidas = 0
        while url and paginas_lidas < max_paginas_por_ano:
            pagina = _fetch_com_retry(url, params=params)
            proposicoes.extend(pagina["dados"])
            proximo = next((l["href"] for l in pagina["links"] if l["rel"] == "next"), None)
            url, params = proximo, None
            paginas_lidas += 1
    return proposicoes


def fetch_proposicoes_por_autor(deputado_id: int, nome_deputado: str) -> list[dict]:
    """Busca proposições de um deputado específico - permite responder 'o que X propôs'."""
    url = f"{BASE_URL}/proposicoes"
    params = {"idDeputadoAutor": deputado_id, "itens": 100, "ordem": "DESC", "ordenarPor": "id"}
    resultado = []
    while url:
        pagina = _fetch_com_retry(url, params=params)
        for p in pagina["dados"]:
            p["autor"] = nome_deputado
        resultado.extend(pagina["dados"])
        url = next((l["href"] for l in pagina["links"] if l["rel"] == "next"), None)
        params = None
    return resultado


def construir_documentos(proposicoes: list[dict]) -> list[Document]:
    """Converte proposições em Documents do LangChain, com metadados para citação."""
    documentos = []
    for p in proposicoes:
        if not p.get("ementa"):
            continue
        texto = f"{p['siglaTipo']} {p['numero']}/{p['ano']}: {p['ementa']}"
        documentos.append(Document(
            page_content=texto,
            metadata={
                "id": p["id"],
                "tipo": p["siglaTipo"],
                "numero": p["numero"],
                "ano": p["ano"],
                "uri": p["uri"].replace("api/v2/proposicoes", "propostas-legislativas/-/proposicao"),
                "autor": p.get("autor", "não identificado"),
            },
        ))
    return documentos


def dividir_em_chunks(documentos: list[Document]) -> list[Document]:
    """Ementas costumam ser curtas, mas algumas são longas - divide por segurança."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    return splitter.split_documents(documentos)


def construir_indice(documentos: list[Document]) -> FAISS:
    embeddings = HuggingFaceEmbeddings(model_name=MODELO_EMBEDDING)
    return FAISS.from_documents(documentos, embeddings)


def salvar_indice(indice: FAISS, caminho: str = CAMINHO_INDICE) -> None:
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    indice.save_local(caminho)


def carregar_indice(caminho: str = CAMINHO_INDICE) -> FAISS:
    embeddings = HuggingFaceEmbeddings(model_name=MODELO_EMBEDDING)
    return FAISS.load_local(caminho, embeddings, allow_dangerous_deserialization=True)


_tokenizer_geracao = None
_modelo_geracao = None


def _get_gerador():
    global _tokenizer_geracao, _modelo_geracao
    if _modelo_geracao is None:
        _tokenizer_geracao = AutoTokenizer.from_pretrained(MODELO_GERACAO)
        _modelo_geracao = AutoModelForSeq2SeqLM.from_pretrained(MODELO_GERACAO)
    return _tokenizer_geracao, _modelo_geracao


def _gerar_texto(prompt: str) -> str:
    tokenizer, modelo = _get_gerador()
    entradas = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
    saida = modelo.generate(**entradas, max_new_tokens=150)
    return tokenizer.decode(saida[0], skip_special_tokens=True)


def responder(pergunta: str, indice: FAISS, k: int = 4) -> RespostaRAG:
    """Busca, mede confiança, recusa se necessário, gera resposta citando as fontes reais."""
    resultados = indice.similarity_search_with_score(pergunta, k=k)

    if not resultados:
        return RespostaRAG("Não encontrei nenhuma proposição relevante para essa pergunta.", 0.0, [], True)

    # FAISS retorna distância L2 (menor = mais parecido) - convertida numa confiança 0-1
    distancia_mais_proxima = resultados[0][1]
    confianca = max(0.0, 1 - distancia_mais_proxima / DISTANCIA_MAXIMA_RELEVANTE)

    if confianca < LIMIAR_CONFIANCA:
        return RespostaRAG(
            "Não tenho confiança suficiente pra responder com base nas proposições que encontrei. "
            "Recomendo checar diretamente no site da Câmara dos Deputados.",
            confianca, [], True,
        )

    contexto = "\n".join(doc.page_content for doc, _ in resultados)
    prompt = (
        f"Com base nas proposições legislativas abaixo, responda a pergunta em português, "
        f"de forma objetiva e curta.\n\nProposições:\n{contexto}\n\nPergunta: {pergunta}\nResposta:"
    )
    saida = _gerar_texto(prompt)

    fontes = [
        {
            "tipo_numero_ano": f"{doc.metadata['tipo']} {doc.metadata['numero']}/{doc.metadata['ano']}",
            "autor": doc.metadata["autor"],
            "uri": doc.metadata["uri"],
        }
        for doc, _ in resultados
    ]

    return RespostaRAG(saida, confianca, fontes, False)
