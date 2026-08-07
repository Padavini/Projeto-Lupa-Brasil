"""Treina e persiste os artefatos usados pela API: pipeline de pré-processamento
e modelo de perfil de gasto (cluster). Rodar sempre que o dado subjacente mudar
de forma relevante.
"""

import sys

sys.path.append(".")

import joblib
import pandas as pd

from src.lupa.db import get_engine
from src.lupa.features import ModeloPerfilGasto, construir_perfil_gasto
from src.preprocessing import construir_pipeline_preprocessamento

CAMINHO_PREPROCESSADOR = "models/preprocessador.joblib"
CAMINHO_MODELO_PERFIL = "models/modelo_perfil_gasto.joblib"


def main() -> None:
    engine = get_engine()

    query_despesas = """
        SELECT
            f.deputado_id, d.sigla_partido AS partido, d.sigla_uf AS uf,
            c.tipo_despesa AS categoria, f.valor_documento, f.valor_glosa
        FROM fact_despesas f
        JOIN dim_deputado d ON d.id = f.deputado_id
        LEFT JOIN dim_categoria_despesa c ON c.id_categoria = f.id_categoria
    """
    despesas = pd.read_sql(query_despesas, engine)

    print("Ajustando pipeline de pré-processamento...")
    preprocessador = construir_pipeline_preprocessamento()
    preprocessador.fit(despesas)
    joblib.dump(preprocessador, CAMINHO_PREPROCESSADOR)
    print(f"Salvo em {CAMINHO_PREPROCESSADOR}")

    print("Ajustando modelo de perfil de gasto (K-Means)...")
    perfil = construir_perfil_gasto(despesas)
    modelo_perfil = ModeloPerfilGasto(n_clusters=4).fit(perfil)
    modelo_perfil.salvar(CAMINHO_MODELO_PERFIL)
    print(f"Salvo em {CAMINHO_MODELO_PERFIL}")


if __name__ == "__main__":
    main()
