"""Testes de src/preprocessing.py - foco em corretude do target e ausência de leakage."""

import pandas as pd
import pytest

from src.preprocessing import (
    construir_pipeline_preprocessamento,
    criar_target,
    split_out_of_time,
)


def _df_exemplo() -> pd.DataFrame:
    return pd.DataFrame({
        "categoria": ["COMBUSTIVEL", "TELEFONIA", "COMBUSTIVEL", "PASSAGEM", "TELEFONIA"],
        "partido": ["PL", "PT", "PL", "PP", "PT"],
        "uf": ["SP", "AM", "SP", "RR", "AM"],
        "valor_documento": [100.0, 200.0, 150.0, 300.0, 50.0],
        "valor_glosa": [0.0, 10.0, 0.0, 0.0, 5.0],
        "ano": [2023, 2023, 2024, 2024, 2025],
        "mes": [1, 6, 3, 11, 2],
    })


def test_criar_target_reflete_valor_glosa():
    df = criar_target(_df_exemplo())
    assert df["houve_glosa"].tolist() == [0, 1, 0, 0, 1]


def test_split_out_of_time_nao_sobrepoe_periodo():
    df = criar_target(_df_exemplo())
    treino, teste = split_out_of_time(df, ano_corte=2024, mes_corte=6)

    periodo_treino = list(zip(treino["ano"], treino["mes"]))
    periodo_teste = list(zip(teste["ano"], teste["mes"]))

    ultimo_periodo_treino = max(periodo_treino)
    primeiro_periodo_teste = min(periodo_teste)

    assert ultimo_periodo_treino < primeiro_periodo_teste, (
        "Vazamento temporal: existe linha no treino com data >= alguma linha do teste"
    )


def test_split_out_of_time_nao_e_aleatorio():
    """Rodar o split duas vezes com o mesmo corte tem que dar exatamente o mesmo resultado -
    provando que não há embaralhamento aleatório envolvido."""
    df = criar_target(_df_exemplo())
    treino1, teste1 = split_out_of_time(df, ano_corte=2024, mes_corte=6)
    treino2, teste2 = split_out_of_time(df, ano_corte=2024, mes_corte=6)

    pd.testing.assert_frame_equal(treino1, treino2)
    pd.testing.assert_frame_equal(teste1, teste2)


def test_pipeline_ajustado_so_no_treino_nao_ve_dado_de_teste():
    """O scaler/encoder devem ser ajustados (fit) só com dado de treino - garante que
    estatísticas do teste (que no mundo real ainda não existem) não vazam pro pré-processamento."""
    df = criar_target(_df_exemplo())
    treino, teste = split_out_of_time(df, ano_corte=2024, mes_corte=6)

    pipeline = construir_pipeline_preprocessamento()
    pipeline.fit(treino)

    media_valor_documento_treino = treino["valor_documento"].mean()
    scaler_ajustado = pipeline.named_transformers_["num"].named_steps["scaler"]

    assert scaler_ajustado.mean_[0] == pytest.approx(media_valor_documento_treino), (
        "O scaler não deveria ter sido ajustado com a média do treino - "
        "possível vazamento de dado do teste no fit"
    )

    # aplicar no teste não deve levantar erro nem re-ajustar o pipeline
    transformado = pipeline.transform(teste)
    assert transformado.shape[0] == len(teste)
