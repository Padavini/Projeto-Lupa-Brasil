"""Teste de integração ponta a ponta do endpoint /deputado/{nome}/resumo.

Precisa do Postgres local rodando e dos artefatos treinados
(scripts/treinar_artefatos.py) - pula automaticamente se algo faltar,
em vez de quebrar o CI quando essa infraestrutura não está disponível.
"""

import os

import pytest
from fastapi.testclient import TestClient

from src.lupa.db import get_engine

CAMINHO_PREPROCESSADOR = "models/preprocessador.joblib"
CAMINHO_MODELO_PERFIL = "models/modelo_perfil_gasto.joblib"


def _infraestrutura_disponivel() -> bool:
    if not (os.path.exists(CAMINHO_PREPROCESSADOR) and os.path.exists(CAMINHO_MODELO_PERFIL)):
        return False
    try:
        with get_engine().connect():
            return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _infraestrutura_disponivel(),
    reason="Postgres local e/ou artefatos treinados (models/) não disponíveis",
)


@pytest.fixture(scope="module")
def client():
    from api.main import app

    with TestClient(app) as test_client:
        yield test_client


def test_resumo_deputado_responde_tudo_num_payload(client):
    resposta = client.get("/deputado/Acácio Favacho/resumo")
    assert resposta.status_code == 200

    corpo = resposta.json()
    assert corpo["nome"] == "Acácio Favacho"
    assert corpo["gasto_total"] > 0
    assert 1 <= corpo["ranking_posicao"] <= corpo["ranking_total"]
    assert "persona" in corpo["perfil"]
    assert 0.0 <= corpo["risco_glosa"]["probabilidade"] <= 1.0
    assert (
        len(corpo["risco_glosa"]["fatores"]) > 0
    ), "risco sem explicação - viola principio de responsabilidade"
    assert isinstance(corpo["proposicoes_recentes"], list)
    assert "disclaimer" in corpo


def test_deputado_inexistente_retorna_404(client):
    resposta = client.get("/deputado/Nome Que Nao Existe De Verdade Nunca/resumo")
    assert resposta.status_code == 404
