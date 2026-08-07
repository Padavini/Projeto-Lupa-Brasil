"""Construção de features e perfil de gasto por deputado (Módulo 8, refatorado)."""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

TOP_CATEGORIAS_PADRAO = [
    "PASSAGEM AÉREA - SIGEPA",
    "DIVULGAÇÃO DA ATIVIDADE PARLAMENTAR.",
    "LOCAÇÃO OU FRETAMENTO DE VEÍCULOS AUTOMOTORES",
    "MANUTENÇÃO DE ESCRITÓRIO DE APOIO À ATIVIDADE PARLAMENTAR",
    "COMBUSTÍVEIS E LUBRIFICANTES.",
    "HOSPEDAGEM ,EXCETO DO PARLAMENTAR NO DISTRITO FEDERAL.",
    "TELEFONIA",
    "LOCAÇÃO OU FRETAMENTO DE AERONAVES",
]

NOMES_PERSONA = {
    0: "Perfil equilibrado",
    1: "Perfil divulgador (alto gasto em divulgação)",
    2: "Perfil viajante (alto gasto em passagem aérea)",
    3: "Perfil operacional (locação/manutenção de escritório)",
}


def construir_perfil_gasto(
    despesas: pd.DataFrame, top_categorias: list[str] = TOP_CATEGORIAS_PADRAO
) -> pd.DataFrame:
    """Transforma despesas (linha por despesa) em perfil de gasto (linha por deputado).

    Cada coluna de categoria vira a proporção do gasto total do deputado
    naquela categoria - não o valor absoluto (Módulo 8).
    """
    df = despesas.copy()
    df["categoria_agrupada"] = df["categoria"].where(df["categoria"].isin(top_categorias), "OUTRAS")

    pivot = df.pivot_table(
        index="deputado_id",
        columns="categoria_agrupada",
        values="valor_documento",
        aggfunc="sum",
        fill_value=0,
    )
    perfil = pivot.div(pivot.sum(axis=1), axis=0)
    perfil["gasto_total"] = pivot.sum(axis=1)
    return perfil


class ModeloPerfilGasto:
    """Agrupa deputados em personas de gasto (K-Means sobre o perfil, Módulo 8)."""

    def __init__(self, n_clusters: int = 4, random_state: int = 42) -> None:
        self.scaler = StandardScaler()
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
        self.colunas_: list[str] | None = None

    def fit(self, perfil: pd.DataFrame) -> "ModeloPerfilGasto":
        self.colunas_ = list(perfil.columns)
        X = self.scaler.fit_transform(perfil.values)
        self.kmeans.fit(X)
        return self

    def predict(self, perfil: pd.DataFrame) -> np.ndarray:
        perfil_alinhado = perfil.reindex(columns=self.colunas_, fill_value=0)
        X = self.scaler.transform(perfil_alinhado.values)
        return self.kmeans.predict(X)

    def nome_persona(self, cluster: int) -> str:
        return NOMES_PERSONA.get(cluster, f"Cluster {cluster}")

    def salvar(self, caminho: str) -> None:
        Path(caminho).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, caminho)

    @staticmethod
    def carregar(caminho: str) -> "ModeloPerfilGasto":
        return joblib.load(caminho)
