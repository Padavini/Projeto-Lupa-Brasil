"""Pré-processamento para modelagem de houve_glosa - Módulo 5."""

from datetime import date

import pandas as pd
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sqlalchemy import Engine, create_engine

COLUNAS_NUMERICAS = ["valor_documento"]
COLUNAS_CATEGORICAS = ["categoria", "partido", "uf"]


def get_engine() -> Engine:
    return create_engine("postgresql+psycopg2://lupa:lupa_dev_local@localhost:5432/lupa_camara")


def carregar_dados(engine: Engine) -> pd.DataFrame:
    """Carrega despesas com as features e o valor_glosa bruto (target ainda não criado)."""
    query = """
        SELECT
            f.id_despesa,
            d.sigla_partido AS partido,
            d.sigla_uf AS uf,
            c.tipo_despesa AS categoria,
            f.valor_documento,
            f.valor_glosa,
            t.ano,
            t.mes
        FROM fact_despesas f
        JOIN dim_deputado d ON d.id = f.deputado_id
        JOIN dim_tempo t ON t.id_tempo = f.id_tempo
        LEFT JOIN dim_categoria_despesa c ON c.id_categoria = f.id_categoria
    """
    return pd.read_sql(query, engine)


def criar_target(df: pd.DataFrame) -> pd.DataFrame:
    """Cria a coluna binária houve_glosa a partir de valor_glosa."""
    df = df.copy()
    df["houve_glosa"] = (df["valor_glosa"] > 0).astype(int)
    return df


def split_out_of_time(
    df: pd.DataFrame, ano_corte: int, mes_corte: int
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Divide treino/teste por data, nunca aleatoriamente.

    Treino: tudo antes de (ano_corte, mes_corte).
    Teste: (ano_corte, mes_corte) em diante.
    """
    corte = (df["ano"] < ano_corte) | ((df["ano"] == ano_corte) & (df["mes"] < mes_corte))
    treino = df[corte]
    teste = df[~corte]
    return treino, teste


def construir_pipeline_preprocessamento() -> ColumnTransformer:
    """Pipeline de scaling + encoding + tratamento de ausentes."""
    transformador_numerico = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])
    transformador_categorico = Pipeline([
        ("imputer", SimpleImputer(strategy="constant", fill_value="desconhecido")),
        ("encoder", OneHotEncoder(handle_unknown="ignore")),
    ])
    return ColumnTransformer([
        ("num", transformador_numerico, COLUNAS_NUMERICAS),
        ("cat", transformador_categorico, COLUNAS_CATEGORICAS),
    ])


def comparar_balanceamento(X_treino, y_treino) -> dict[str, dict[int, int]]:
    """Compara distribuição de classes antes/depois de cada estratégia de balanceamento."""
    resultados = {"original": dict(y_treino.value_counts())}

    X_smote, y_smote = SMOTE(random_state=42).fit_resample(X_treino, y_treino)
    resultados["smote"] = dict(pd.Series(y_smote).value_counts())

    X_under, y_under = RandomUnderSampler(random_state=42).fit_resample(X_treino, y_treino)
    resultados["undersampling"] = dict(pd.Series(y_under).value_counts())

    resultados["class_weight"] = {
        "nota": "sem resample; passar class_weight='balanced' ao classificador"
    }

    return resultados


if __name__ == "__main__":
    engine = get_engine()
    df = carregar_dados(engine)
    df = criar_target(df)

    proporcao = df["houve_glosa"].mean() * 100
    print(f"Proporção real de houve_glosa: {proporcao:.3f}%")

    hoje = date.today()
    treino, teste = split_out_of_time(df, hoje.year, hoje.month - 3 if hoje.month > 3 else 1)
    print(f"Treino: {len(treino)} linhas | Teste: {len(teste)} linhas")
