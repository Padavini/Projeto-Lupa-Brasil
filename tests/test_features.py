"""Testes unitários de src/lupa/features.py - sem tocar no banco."""

import pandas as pd

from src.lupa.features import ModeloPerfilGasto, construir_perfil_gasto


def _despesas_exemplo() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "deputado_id": [1, 1, 1, 2, 2, 3],
            "partido": ["PL", "PL", "PL", "PT", "PT", "PP"],
            "uf": ["SP", "SP", "SP", "RJ", "RJ", "MG"],
            "categoria": [
                "PASSAGEM AÉREA - SIGEPA",
                "PASSAGEM AÉREA - SIGEPA",
                "TELEFONIA",
                "DIVULGAÇÃO DA ATIVIDADE PARLAMENTAR.",
                "DIVULGAÇÃO DA ATIVIDADE PARLAMENTAR.",
                "OUTRA CATEGORIA QUALQUER",
            ],
            "valor_documento": [1000.0, 500.0, 100.0, 2000.0, 2000.0, 50.0],
        }
    )


def test_construir_perfil_soma_proporcoes_um():
    perfil = construir_perfil_gasto(_despesas_exemplo())
    colunas_categoria = [c for c in perfil.columns if c != "gasto_total"]
    somas = perfil[colunas_categoria].sum(axis=1)
    assert (somas.round(6) == 1.0).all()


def test_construir_perfil_categoria_fora_do_top_vira_outras():
    perfil = construir_perfil_gasto(_despesas_exemplo())
    assert "OUTRAS" in perfil.columns
    assert perfil.loc[3, "OUTRAS"] == 1.0


def test_construir_perfil_gasto_total_correto():
    perfil = construir_perfil_gasto(_despesas_exemplo())
    assert perfil.loc[1, "gasto_total"] == 1600.0
    assert perfil.loc[2, "gasto_total"] == 4000.0


def test_modelo_perfil_predict_retorna_um_cluster_por_linha():
    perfil = construir_perfil_gasto(_despesas_exemplo())
    modelo = ModeloPerfilGasto(n_clusters=2).fit(perfil)
    clusters = modelo.predict(perfil)
    assert len(clusters) == len(perfil)


def test_modelo_perfil_salvar_e_carregar(tmp_path):
    perfil = construir_perfil_gasto(_despesas_exemplo())
    modelo = ModeloPerfilGasto(n_clusters=2).fit(perfil)
    caminho = tmp_path / "modelo.joblib"

    modelo.salvar(str(caminho))
    modelo_carregado = ModeloPerfilGasto.carregar(str(caminho))

    assert (modelo_carregado.predict(perfil) == modelo.predict(perfil)).all()
