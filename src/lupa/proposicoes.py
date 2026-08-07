"""Consulta de proposições recentes de um deputado - API direta, sem RAG."""

import requests

BASE_URL = "https://dadosabertos.camara.leg.br/api/v2"


def buscar_proposicoes_recentes(deputado_id: int, limite: int = 5) -> list[dict[str, str | int]]:
    """Últimas `limite` proposições de autoria do deputado, mais recentes primeiro."""
    params = {
        "idDeputadoAutor": deputado_id,
        "itens": limite,
        "ordem": "DESC",
        "ordenarPor": "id",
    }
    resposta = requests.get(f"{BASE_URL}/proposicoes", params=params, timeout=15)
    resposta.raise_for_status()
    dados = resposta.json()["dados"]
    return [
        {
            "tipo_numero_ano": f"{p['siglaTipo']} {p['numero']}/{p['ano']}",
            "ementa": p["ementa"],
            "uri": p["uri"].replace("api/v2/proposicoes", "propostas-legislativas/-/proposicao"),
        }
        for p in dados
    ]
