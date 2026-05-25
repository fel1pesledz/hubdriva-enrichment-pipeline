from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.pool import SimpleConnectionPool

app = FastAPI(title="Gold Analytics API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


DB_CONFIG = {
    "host": "postgres",
    "database": "dados",
    "user": "admin",
    "password": "admin",
    "port": 5432
}

pool = SimpleConnectionPool(minconn=1, maxconn=10, **DB_CONFIG)

def get_connection():
    return pool.getconn()

def release_connection(conn):
    pool.putconn(conn)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/analytics/overview")
def overview():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT
                COUNT(*) AS total_jobs,
                ROUND(
                    SUM(CASE WHEN status_processamento = 'CONCLUIDO' THEN 1 ELSE 0 END)::numeric
                    / NULLIF(COUNT(*), 0) * 100, 2
                ) AS taxa_sucesso,
                AVG(duracao_processamento_minutos) AS tempo_medio
            FROM gold_enriquecimentos;
        """)
        row = cursor.fetchone()
        return {
            "total_jobs": row[0] or 0,
            "taxa_sucesso": float(row[1]) if row[1] is not None else 0.0,
            "tempo_medio": float(row[2]) if row[2] is not None else 0.0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        release_connection(conn)


@app.get("/analytics/by-status")
def by_status():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT
                status_processamento,
                COUNT(*) as total
            FROM gold_enriquecimentos
            GROUP BY status_processamento;
        """)
        rows = cursor.fetchall()
        return [{"status": r[0], "total": r[1]} for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        release_connection(conn)


@app.get("/analytics/enrichments")
def enrichments(
    nome_workspace: str = Query(None, description="Filtrar pelo nome do workspace"),
    status_processamento: str = Query(None, description="Filtrar pelo status"),
    limit: int = Query(50, ge=1),
    offset: int = Query(0, ge=0)
):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = """
            SELECT id_enriquecimento, nome_workspace, status_processamento, total_contatos, data_criacao
            FROM gold_enriquecimentos
            WHERE 1=1
        """
        params = []

        # Filtro por nome do workspace (substring, case-insensitive)
        if nome_workspace:
            query += " AND nome_workspace ILIKE %s"
            params.append(f"%{nome_workspace}%")

        # Filtro por status
        if status_processamento:
            query += " AND status_processamento = %s"
            params.append(status_processamento)

        # Paginação
        query += " ORDER BY data_criacao DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        cursor.execute(query, params)
        rows = cursor.fetchall()

        return [
            {
                "id_enriquecimento": r[0],
                "nome_workspace": r[1],
                "status_processamento": r[2],
                "total_contatos": r[3],
                "data_criacao": str(r[4])
            }
            for r in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        release_connection(conn)


@app.get("/analytics/workspaces/top")
def top_workspaces(limit: int = Query(10, ge=1)):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f"""
            SELECT
                nome_workspace,
                COUNT(*) AS total_enrichments,
                SUM(total_contatos) AS total_contatos
            FROM gold_enriquecimentos
            GROUP BY nome_workspace
            ORDER BY total_enrichments DESC
            LIMIT {limit}
        """)
        rows = cursor.fetchall()
        return [
            {
                "nome_workspace": r[0],
                "total_enrichments": r[1],
                "total_contatos": r[2]
            }
            for r in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        release_connection(conn)
