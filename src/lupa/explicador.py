"""Explicação SHAP do risco de glosa, em linguagem acessível (Módulo 7)."""

import numpy as np
import pandas as pd
import shap
from sklearn.compose import ColumnTransformer


class ExplicadorRisco:
    """Nunca deixa o risco de glosa ser exibido sem uma explicação ao lado."""

    def __init__(self, modelo_lightgbm, preprocessador: ColumnTransformer) -> None:
        self.explicador = shap.TreeExplainer(modelo_lightgbm)
        self.preprocessador = preprocessador
        self.nomes_features = preprocessador.get_feature_names_out()

    def explicar(self, despesa: pd.DataFrame, top_n: int = 3) -> list[dict[str, str | float]]:
        """Retorna os `top_n` fatores que mais pesaram na previsão, com direção e magnitude."""
        X = self.preprocessador.transform(despesa)
        X_denso = np.asarray(X.todense()) if hasattr(X, "todense") else X
        valores_shap = self.explicador.shap_values(X_denso)[0]

        indices_top = np.argsort(-np.abs(valores_shap))[:top_n]
        fatores = []
        for i in indices_top:
            fatores.append(
                {
                    "fator": self._nome_legivel(self.nomes_features[i]),
                    "direcao": "aumentou" if valores_shap[i] > 0 else "diminuiu",
                    "impacto": round(float(valores_shap[i]), 3),
                }
            )
        return fatores

    @staticmethod
    def _nome_legivel(nome_feature: str) -> str:
        """'cat__categoria_TELEFONIA' -> 'categoria: TELEFONIA' - sem jargão técnico de encoding."""
        nome = nome_feature.split("__", 1)[-1]
        if "_" in nome:
            campo, valor = nome.split("_", 1)
            return f"{campo}: {valor}"
        return nome
