from fastapi import FastAPI, Header, HTTPException
from uuid import uuid4
from datetime import datetime, timedelta, timezone
import random
import time

TOTAL_ITENS: int = 1000

app = FastAPI()

API_KEY = "driva_test_key_abc123xyz789"

RATE_LIMIT = 8
WINDOW_SECONDS = 10
RETRY_AFTER = 3

request_count = 0
window_start = time.time()

WORKSPACE_NAMES = [
    "Tech Corp",
    "Data Labs",
    "Alpha Systems",
    "NextGen Corp",
    "Cloudify",
    "Insight Analytics",
    "Blue Ocean",
    "Nova Digital",
    "Bright AI",
    "Vertex Group"
]

def gerar_registro_sujo():
    """Gera um registro com chance de ter dados inconsistentes."""
    problema = random.choices(
        ["ok", "total_contacts_nulo", "total_contacts_negativo",
         "status_invalido", "contact_type_invalido",
         "workspace_nulo", "data_invertida", "campo_faltando"],
        weights=[60, 7, 5, 7, 5, 5, 6, 5],
        k=1
    )[0]

    created = datetime.now() - timedelta(minutes=random.randint(1, 30))
    updated = created + timedelta(minutes=random.randint(1, 30))

    # Data invertida: updated antes de created
    if problema == "data_invertida":
        created, updated = updated, created

    # Timezone inconsistente em ~20% dos registros ok
    if problema == "ok" and random.random() < 0.2:
        created = created.replace(tzinfo=timezone.utc)
        updated = updated.replace(tzinfo=timezone.utc)

    registro = {
        "id": str(uuid4()),
        "id_workspace": str(uuid4()),
        "workspace_name": random.choice(WORKSPACE_NAMES),
        "total_contacts": random.randint(10, 2000),
        "contact_type": random.choice(["PERSON", "COMPANY"]),
        "status": random.choice(["COMPLETED", "FAILED", "PROCESSING", "CANCELED"]),
        "created_at": created.isoformat(),
        "updated_at": updated.isoformat()
    }

    # Aplica o problema sorteado
    if problema == "total_contacts_nulo":
        registro["total_contacts"] = None

    elif problema == "total_contacts_negativo":
        registro["total_contacts"] = random.randint(-500, -1)

    elif problema == "status_invalido":
        registro["status"] = random.choice(["PENDING", "UNKNOWN", "ERRO", "", None])

    elif problema == "contact_type_invalido":
        registro["contact_type"] = random.choice(["LEAD", "CLIENT", "", None])

    elif problema == "workspace_nulo":
        registro["workspace_name"] = random.choice([None, "", "  "])

    elif problema == "campo_faltando":
        campo = random.choice(["workspace_name", "contact_type", "total_contacts"])
        del registro[campo]

    return registro


@app.get("/people/v1/enrichments")
def get_enrichments(
    page: int = 1,
    limit: int = 50,
    authorization: str = Header(None)
):
    global request_count, window_start

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")

    token = authorization.replace("Bearer ", "")
    if token != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    now = time.time()
    if now - window_start > WINDOW_SECONDS:
        request_count = 0
        window_start = now

    request_count += 1

    if request_count > RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail="Too Many Requests",
            headers={"Retry-After": str(RETRY_AFTER)}
        )

    if limit < 1 or limit > 100:
        raise HTTPException(status_code=400, detail="Limit must be between 1 and 100")

    total_pages = (TOTAL_ITENS + limit - 1) // limit

    if page < 1 or page > total_pages:
        raise HTTPException(status_code=400, detail="Page out of range")

    meta = {
        "current_page": page,
        "items_per_page": limit,
        "total_items": TOTAL_ITENS,
        "total_pages": total_pages
    }

    start_index = (page - 1) * limit
    end_index = min(start_index + limit, TOTAL_ITENS)

    data = [gerar_registro_sujo() for _ in range(start_index, end_index)]

    return {
        "meta": meta,
        "data": data
    }
