"""Conexão com o Postgres do projeto."""

import os

from sqlalchemy import Engine, create_engine


def get_engine() -> Engine:
    """Cria a engine de conexão com o Postgres.

    Lê de variáveis de ambiente quando presentes, com os valores do
    docker-compose local como default - evita hardcode de credencial.
    """
    usuario = os.environ.get("LUPA_DB_USER", "lupa")
    senha = os.environ.get("LUPA_DB_PASSWORD", "lupa_dev_local")
    host = os.environ.get("LUPA_DB_HOST", "localhost")
    porta = os.environ.get("LUPA_DB_PORT", "5432")
    nome_banco = os.environ.get("LUPA_DB_NAME", "lupa_camara")
    return create_engine(f"postgresql+psycopg2://{usuario}:{senha}@{host}:{porta}/{nome_banco}")
