"""Testes unitários dos contratos Pydantic - garante a regra de responsabilidade
'nunca risco sem explicação' no nível do próprio schema."""

import pytest
from pydantic import ValidationError

from src.lupa.schemas import ClusterPerfil, FatorRisco, Proposicao, ResumoDeputado, RiscoGlosa


def _risco_valido() -> RiscoGlosa:
    return RiscoGlosa(
        probabilidade=0.3,
        baseado_em="despesa mais recente",
        fatores=[FatorRisco(fator="categoria: TELEFONIA", direcao="aumentou", impacto=0.5)],
    )


def test_risco_glosa_probabilidade_fora_do_intervalo_falha():
    with pytest.raises(ValidationError):
        RiscoGlosa(probabilidade=1.5, baseado_em="x", fatores=[])


def test_risco_glosa_aceita_probabilidade_valida():
    risco = _risco_valido()
    assert 0.0 <= risco.probabilidade <= 1.0


def test_resumo_deputado_sempre_tem_disclaimer_por_padrao():
    resumo = ResumoDeputado(
        deputado_id=1,
        nome="Fulano",
        partido="PP",
        uf="SP",
        gasto_total=1000.0,
        ranking_posicao=1,
        ranking_total=100,
        perfil=ClusterPerfil(cluster_id=0, persona="Perfil equilibrado"),
        risco_glosa=_risco_valido(),
        proposicoes_recentes=[
            Proposicao(tipo_numero_ano="PL 1/2024", ementa="...", uri="http://x")
        ],
    )
    assert "não uma acusação" in resumo.disclaimer
