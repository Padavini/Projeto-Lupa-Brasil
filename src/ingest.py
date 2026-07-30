"""Ingestão paginada da API de Dados Abertos da Câmara dos Deputados.

Módulo 2 - grava dado bruto (raw) no Postgres. O star schema
(fact_despesas, dim_*) vem depois, num passo separado.
"""

import os
import time
from datetime import date
from typing import Any, Iterator

import psycopg2
import requests

BASE_URL = "https://dadosabertos.camara.leg.br/api/v2"

# eleição atual (2022) até o ano corrente - não busca despesas anteriores
ANO_INICIAL = 2022

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": os.environ.get("LUPA_DB_USER", "lupa"),
    "password": os.environ.get("LUPA_DB_PASSWORD", "lupa_dev_local"),
    "dbname": os.environ.get("LUPA_DB_NAME", "lupa_camara"),
}


def fetch_with_retry(
    url: str, params: dict[str, Any] | None = None, max_retries: int = 3
) -> dict[str, Any]:
    """Faz GET em `url`, tentando de novo com backoff se a rede falhar."""
    # tenta no máximo `max_retries` vezes antes de desistir de vez
    for tentativa in range(1, max_retries + 1):
        try:
            # o pedido em si - "timeout" evita ficar esperando pra sempre
            # se o servidor simplesmente não responder
            response = requests.get(url, params=params, timeout=10)
            # se o servidor respondeu com erro (404, 500...), interrompe aqui
            # e cai no "except" - sem isso, um erro passaria despercebido
            response.raise_for_status()
            # deu tudo certo: decodifica o JSON e sai da função na hora
            return response.json()
        except requests.exceptions.RequestException:
            # essa era a última tentativa permitida? desiste e propaga o erro
            if tentativa == max_retries:
                raise
            # senão, espera um pouco mais a cada tentativa (backoff) e repete
            # o loop: 2s na 1ª falha, 4s na 2ª, etc.
            time.sleep(tentativa * 2)


def fetch_paginated(
    endpoint: str, params: dict[str, Any] | None = None
) -> Iterator[dict[str, Any]]:
    """Percorre todas as páginas de `endpoint`, entregando 1 item por vez."""
    url = f"{BASE_URL}{endpoint}"
    # continua repetindo enquanto existir uma próxima página (url != None)
    while url:
        # busca só a página atual, com toda a proteção de fetch_with_retry
        pagina = fetch_with_retry(url, params=params)

        # entrega um item de cada vez pra quem está usando essa função,
        # em vez de montar uma lista gigante com tudo na memória
        for item in pagina["dados"]:
            yield item

        # procura, na lista de links, o que tem rel == "next" (o "bilhete"
        # dizendo onde buscar a próxima página); se não achar, vira None
        proximo = next(
            (link["href"] for link in pagina["links"] if link["rel"] == "next"),
            None,
        )
        url = proximo  # None encerra o "while"; um endereço continua o loop
        params = None  # a URL de "next" já vem com os parâmetros embutidos


def create_raw_tables(conn: psycopg2.extensions.connection) -> None:
    """Cria as tabelas raw_* se ainda não existirem."""
    # um "cursor" é o objeto que de fato envia comandos SQL pro Postgres
    # e recebe as respostas - pensa nele como o "microfone" da conexão
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS raw_deputados (
                id INTEGER PRIMARY KEY,
                nome TEXT,
                sigla_partido TEXT,
                sigla_uf TEXT,
                id_legislatura INTEGER
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS raw_despesas (
                cod_documento TEXT,
                num_documento TEXT,
                deputado_id INTEGER,
                ano INTEGER,
                mes INTEGER,
                tipo_despesa TEXT,
                data_documento TIMESTAMP,
                valor_documento NUMERIC,
                valor_liquido NUMERIC,
                valor_glosa NUMERIC,
                nome_fornecedor TEXT,
                cnpj_cpf_fornecedor TEXT,
                -- cod_documento sozinho não é único: a API usa "0" como
                -- placeholder para despesas sem nota fiscal (ex.: telefonia).
                -- a combinação dos 3 campos abaixo é que garante unicidade.
                PRIMARY KEY (deputado_id, cod_documento, num_documento)
            )
            """
        )
    # nada do que rodamos acima é gravado de fato até dar o "commit" -
    # é o mesmo conceito do git: as tabelas ficam "propostas" até confirmar
    conn.commit()


def upsert_deputados(
    conn: psycopg2.extensions.connection, deputados: Iterator[dict[str, Any]]
) -> int:
    """Grava cada deputado em raw_deputados, sem duplicar ao rodar de novo."""
    total = 0
    with conn.cursor() as cur:
        for d in deputados:
            cur.execute(
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
    conn.commit()
    return total


def upsert_despesas(
    conn: psycopg2.extensions.connection,
    deputado_id: int,
    despesas: Iterator[dict[str, Any]],
) -> int:
    """Grava cada despesa em raw_despesas, sem duplicar ao rodar de novo."""
    total = 0
    with conn.cursor() as cur:
        for despesa in despesas:
            # a despesa que vem da API não sabe de quem ela é - o
            # deputado_id chega separado, como parâmetro da função.
            # por isso juntamos os dois num único dicionário aqui
            params = {**despesa, "deputado_id": deputado_id}
            cur.execute(
                """
                INSERT INTO raw_despesas (
                    cod_documento, num_documento, deputado_id, ano, mes, tipo_despesa,
                    data_documento, valor_documento, valor_liquido,
                    valor_glosa, nome_fornecedor, cnpj_cpf_fornecedor
                )
                VALUES (
                    %(codDocumento)s, %(numDocumento)s, %(deputado_id)s, %(ano)s, %(mes)s, %(tipoDespesa)s,
                    %(dataDocumento)s, %(valorDocumento)s, %(valorLiquido)s,
                    %(valorGlosa)s, %(nomeFornecedor)s, %(cnpjCpfFornecedor)s
                )
                ON CONFLICT (deputado_id, cod_documento, num_documento) DO UPDATE SET
                    ano = EXCLUDED.ano,
                    mes = EXCLUDED.mes,
                    tipo_despesa = EXCLUDED.tipo_despesa,
                    data_documento = EXCLUDED.data_documento,
                    valor_documento = EXCLUDED.valor_documento,
                    valor_liquido = EXCLUDED.valor_liquido,
                    valor_glosa = EXCLUDED.valor_glosa,
                    nome_fornecedor = EXCLUDED.nome_fornecedor,
                    cnpj_cpf_fornecedor = EXCLUDED.cnpj_cpf_fornecedor
                """,
                params,
            )
            total += 1
    conn.commit()
    return total


def main() -> None:
    """Orquestra o pipeline completo: deputados + despesas de cada um."""
    conn = psycopg2.connect(**DB_CONFIG)
    create_raw_tables(conn)

    # busca a lista de deputados uma vez só, e já materializa em lista -
    # precisamos saber o total antes de começar o loop, pra imprimir o progresso
    deputados = list(fetch_paginated("/deputados"))
    upsert_deputados(conn, iter(deputados))
    print(f"{len(deputados)} deputados gravados")

    # agora, um deputado de cada vez, busca e grava as despesas dele -
    # um ano por vez, de ANO_INICIAL até o ano corrente, usando o filtro
    # "ano" que a própria API oferece (assim não baixamos despesas de
    # legislaturas anteriores, que não interessam a este projeto)
    ano_corrente = date.today().year
    for i, deputado in enumerate(deputados, start=1):
        total_despesas = 0
        for ano in range(ANO_INICIAL, ano_corrente + 1):
            despesas = fetch_paginated(
                f"/deputados/{deputado['id']}/despesas", params={"ano": ano}
            )
            total_despesas += upsert_despesas(conn, deputado["id"], despesas)
        print(f"[{i}/{len(deputados)}] {deputado['nome']}: {total_despesas} despesas")

    conn.close()


if __name__ == "__main__":
    main()
