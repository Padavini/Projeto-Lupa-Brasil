"""Contratos de dado da API - Pydantic."""

from pydantic import BaseModel, Field


class FatorRisco(BaseModel):
    fator: str
    direcao: str
    impacto: float


class RiscoGlosa(BaseModel):
    """Nunca existe risco sem explicação - os dois campos são obrigatórios juntos."""

    probabilidade: float = Field(..., ge=0.0, le=1.0)
    baseado_em: str
    fatores: list[FatorRisco]


class ClusterPerfil(BaseModel):
    cluster_id: int
    persona: str


class Proposicao(BaseModel):
    tipo_numero_ano: str
    ementa: str
    uri: str


class ResumoDeputado(BaseModel):
    deputado_id: int
    nome: str
    partido: str
    uf: str
    gasto_total: float
    ranking_posicao: int
    ranking_total: int
    perfil: ClusterPerfil
    risco_glosa: RiscoGlosa
    proposicoes_recentes: list[Proposicao]
    disclaimer: str = (
        "Dado oficial da API da Câmara dos Deputados. 'Risco' é um indício estatístico "
        "de checagem, não uma acusação nem uma constatação de irregularidade."
    )
