"""API do Projeto Lupa - Módulo 11.

Endpoint consolidado: /deputado/{nome}/resumo - gasto, ranking, perfil de
cluster, risco de glosa explicado (nunca sem SHAP) e proposições recentes.
"""

import sys
from contextlib import asynccontextmanager

sys.path.append(".")

import pandas as pd
from fastapi import FastAPI, HTTPException

from src.lupa.db import get_engine
from src.lupa.explicador import ExplicadorRisco
from src.lupa.features import ModeloPerfilGasto, construir_perfil_gasto
from src.lupa.modelo import ModeloRisco
from src.lupa.proposicoes import buscar_proposicoes_recentes
from src.lupa.schemas import ClusterPerfil, FatorRisco, Proposicao, ResumoDeputado, RiscoGlosa

CAMINHO_PREPROCESSADOR = "models/preprocessador.joblib"
CAMINHO_MODELO_PERFIL = "models/modelo_perfil_gasto.joblib"

recursos: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    recursos["engine"] = get_engine()
    recursos["modelo_perfil"] = ModeloPerfilGasto.carregar(CAMINHO_MODELO_PERFIL)
    recursos["modelo_risco"] = ModeloRisco.carregar(CAMINHO_PREPROCESSADOR)
    recursos["explicador"] = ExplicadorRisco(
        recursos["modelo_risco"].modelo, recursos["modelo_risco"].preprocessador
    )
    yield
    recursos.clear()


app = FastAPI(
    title="Projeto Lupa API",
    description="Painel de transparência sobre gastos e atuação de deputados federais.",
    lifespan=lifespan,
)


@app.get("/deputado/{nome}/resumo", response_model=ResumoDeputado)
def resumo_deputado(nome: str) -> ResumoDeputado:
    engine = recursos["engine"]

    deputado = pd.read_sql(
        "SELECT id, nome, sigla_partido AS partido, sigla_uf AS uf FROM dim_deputado "
        "WHERE nome ILIKE %(nome)s LIMIT 1",
        engine,
        params={"nome": f"%{nome}%"},
    )
    if deputado.empty:
        raise HTTPException(status_code=404, detail=f"Nenhum deputado encontrado para '{nome}'")
    dep = deputado.iloc[0]

    despesas = pd.read_sql(
        """
        SELECT
            f.deputado_id, d.sigla_partido AS partido, d.sigla_uf AS uf,
            c.tipo_despesa AS categoria, f.valor_documento, f.valor_glosa, t.ano, t.mes
        FROM fact_despesas f
        JOIN dim_deputado d ON d.id = f.deputado_id
        JOIN dim_tempo t ON t.id_tempo = f.id_tempo
        LEFT JOIN dim_categoria_despesa c ON c.id_categoria = f.id_categoria
        WHERE f.deputado_id = %(id)s
        ORDER BY t.ano DESC, t.mes DESC
        """,
        engine,
        params={"id": int(dep["id"])},
    )
    if despesas.empty:
        raise HTTPException(status_code=404, detail=f"Sem despesas registradas para '{nome}'")

    gasto_total = float(despesas["valor_documento"].sum())

    gasto_por_deputado = pd.read_sql(
        "SELECT deputado_id, SUM(valor_documento) AS total FROM fact_despesas GROUP BY deputado_id "
        "ORDER BY total DESC",
        engine,
    )
    ranking_posicao = (
        int(gasto_por_deputado.reset_index(drop=True).query("deputado_id == @dep.id").index[0]) + 1
    )
    ranking_total = len(gasto_por_deputado)

    todas_despesas = pd.read_sql(
        """
        SELECT
            f.deputado_id, d.sigla_partido AS partido, d.sigla_uf AS uf,
            c.tipo_despesa AS categoria, f.valor_documento
        FROM fact_despesas f
        JOIN dim_deputado d ON d.id = f.deputado_id
        LEFT JOIN dim_categoria_despesa c ON c.id_categoria = f.id_categoria
        """,
        engine,
    )
    perfil_todos = construir_perfil_gasto(todas_despesas)
    modelo_perfil: ModeloPerfilGasto = recursos["modelo_perfil"]
    cluster_id = int(modelo_perfil.predict(perfil_todos.loc[[dep["id"]]])[0])

    despesa_mais_recente = despesas.iloc[[0]][["categoria", "partido", "uf", "valor_documento"]]
    modelo_risco: ModeloRisco = recursos["modelo_risco"]
    probabilidade = float(modelo_risco.prever_probabilidade(despesa_mais_recente)[0])
    explicador: ExplicadorRisco = recursos["explicador"]
    fatores = explicador.explicar(despesa_mais_recente)

    proposicoes = buscar_proposicoes_recentes(int(dep["id"]), limite=5)

    return ResumoDeputado(
        deputado_id=int(dep["id"]),
        nome=dep["nome"],
        partido=dep["partido"],
        uf=dep["uf"],
        gasto_total=gasto_total,
        ranking_posicao=ranking_posicao,
        ranking_total=ranking_total,
        perfil=ClusterPerfil(cluster_id=cluster_id, persona=modelo_perfil.nome_persona(cluster_id)),
        risco_glosa=RiscoGlosa(
            probabilidade=probabilidade,
            baseado_em="despesa mais recente do deputado",
            fatores=[FatorRisco(**f) for f in fatores],
        ),
        proposicoes_recentes=[Proposicao(**p) for p in proposicoes],
    )
