"""Modelo de risco de glosa (LightGBM do Módulo 7, via MLflow Model Registry)."""

import joblib
import mlflow
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer

NOME_MODELO_REGISTRADO = "lupa-houve-glosa-lightgbm"


class ModeloRisco:
    """Carrega o modelo promovido no registry e o pipeline de pré-processamento."""

    def __init__(self, preprocessador: ColumnTransformer, modelo_lightgbm) -> None:
        self.preprocessador = preprocessador
        self.modelo = modelo_lightgbm

    @classmethod
    def carregar(
        cls,
        caminho_preprocessador: str,
        tracking_uri: str = "sqlite:///mlflow.db",
        versao_modelo: str = "1",
    ) -> "ModeloRisco":
        mlflow.set_tracking_uri(tracking_uri)
        preprocessador = joblib.load(caminho_preprocessador)
        modelo = mlflow.lightgbm.load_model(f"models:/{NOME_MODELO_REGISTRADO}/{versao_modelo}")
        return cls(preprocessador, modelo)

    def prever_probabilidade(self, despesas: pd.DataFrame) -> np.ndarray:
        """Probabilidade de glosa por despesa (colunas: categoria, partido, uf, valor_documento)."""
        X = self.preprocessador.transform(despesas)
        return self.modelo.predict_proba(X)[:, 1]
