"""Ingestão da API de Dados Abertos da Câmara dos Deputados.

Versão em classe do script original (src/ingest.py, Módulo 2) - mesma lógica,
reorganizada para ser importável e testável como parte do pacote instalável.
"""

import time
from collections.abc import Iterator
from typing import Any

import requests
from sqlalchemy import Engine

BASE_URL = "https://dadosabertos.camara.leg.br/api/v2"


class IngestorCamara:
    """Busca e persiste dado bruto da API da Câmara, de forma idempotente."""

    def __init__(self, engine: Engine, base_url: str = BASE_URL, max_retries: int = 3) -> None:
        self.engine = engine
        self.base_url = base_url
        self.max_retries = max_retries

    def fetch_com_retry(self, url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        for tentativa in range(1, self.max_retries + 1):
            try:
                resposta = requests.get(url, params=params, timeout=10)
                resposta.raise_for_status()
                return resposta.json()
            except requests.exceptions.RequestException:
                if tentativa == self.max_retries:
                    raise
                time.sleep(tentativa * 2)

    def fetch_paginado(
        self, endpoint: str, params: dict[str, Any] | None = None
    ) -> Iterator[dict[str, Any]]:
        url = f"{self.base_url}{endpoint}"
        while url:
            pagina = self.fetch_com_retry(url, params=params)
            yield from pagina["dados"]
            url = next((link["href"] for link in pagina["links"] if link["rel"] == "next"), None)
            params = None

    def upsert_deputados(self, deputados: Iterator[dict[str, Any]]) -> int:
        total = 0
        with self.engine.begin() as conn:
            for d in deputados:
                conn.exec_driver_sql(
                    """
                    INSERT INTO raw_deputados (id, nome, sigla_partido, sigla_uf, id_legislatura)
                    VALUES (%(id)s, %(nome)s, %(siglaPartido)s, %(siglaUf)s, %(idLegislatura)s)
                    ON CONFLICT (id) DO UPDATE SET
                        nome = EXCLUDED.nome,
                        sigla_partido = EXCLUDED.sigla_partido,
                        sigla_uf = EXCLUDED.sigla_uf,
                        id_legislatura = EXCLUDED.id_legislatura
                    """,
                    d,
                )
                total += 1
        return total
