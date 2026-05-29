# HubDriva – Data Enrichment Monitoring

Pipeline automatizada de monitoramento de enriquecimentos de dados da plataforma HubDriva. Ingere dados de uma API externa, aplica limpeza e transformações em camadas (Bronze → Silver → Gold) e expõe métricas via API Analytics e Dashboard.

---

## Arquitetura

```
API Fonte (porta 3000)
      │
      ▼
┌─────────────┐
│   BRONZE    │  Dados brutos, sem transformação
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   SILVER    │  Limpeza e validação de qualidade
└──────┬──────┘
       │  
       ▼
┌─────────────┐
│    GOLD     │  Métricas calculadas, campos traduzidos
└──────┬──────┘
       │
       ▼
API Analytics (porta 3001) → Dashboard
```

A orquestração é feita pelo **n8n**, que executa a pipeline a cada 5 minutos via Scheduler.

---

## Estrutura do Projeto

```
hubdriva-enrichment-pipeline/
├── docker-compose.yml
├── init.sql                  # Criação das tabelas no PostgreSQL
├── api_fonte/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── api_fonte.py          # Simula API de enriquecimentos com dados sujos
├── api_analytics/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── api_analytics.py      # Expõe métricas da camada Gold
├── dashboard/
│   └── dashboard.html        # Dashboard de KPIs
└── workflows/
    ├── Data_Injestion.json   # Bronze: ingestão paginada com retry
    ├── Cleaning.json         # Silver: limpeza e validação
    ├── Processing.json       # Gold: transformações e métricas
    └── Scheduler.json        # Orquestrador (executa a cada 5 min)
```

---

## Camadas do Data Warehouse

### Bronze — `bronze_enrichments`
Dados brutos vindos diretamente da API. Nenhuma transformação aplicada. Serve como fonte de verdade para reprocessamento.

### Silver — `silver_enrichments`
Camada de limpeza e validação. Cada registro recebe:
- `registro_valido` — booleano indicando se passou nas validações
- `motivo_invalido` — descrição dos problemas encontrados (ex: `total_contacts negativo; workspace_name vazio`)

Validações aplicadas:
- `workspace_name` não pode ser nulo ou vazio
- `total_contacts` não pode ser nulo ou negativo
- `status` deve ser um dos valores esperados: `COMPLETED`, `FAILED`, `PROCESSING`, `CANCELED`
- `contact_type` deve ser `PERSON` ou `COMPANY`
- `updated_at` não pode ser anterior a `created_at`

### Gold — `gold_enriquecimentos`
Apenas registros válidos da Silver. Transformações aplicadas:
- Campos traduzidos para português
- `duracao_processamento_minutos` e `tempo_por_contato_minutos` calculados
- `categoria_tamanho_job`: `PEQUENO` / `MEDIO` / `GRANDE` / `MUITO_GRANDE`
- `processamento_sucesso` e `necessita_reprocessamento` como booleanos

---

## Pré-requisitos

- Docker e Docker Compose instalados
- Porta 5432 livre (se tiver PostgreSQL local rodando: `sudo systemctl stop postgresql`)

---

## Como Rodar

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/hubdriva-enrichment-pipeline.git
cd hubdriva-enrichment-pipeline
```

### 2. Suba os containers

```bash
docker compose up -d --build
```

### 3. Verifique se tudo está rodando

```bash
docker compose ps
```

Todos os containers devem estar com status `Up`.

### 4. Confirme as tabelas no banco

```bash
docker exec -it postgres psql -U admin -d dados -c "\dt"
```

Esperado: `bronze_enrichments`, `silver_enrichments`, `gold_enriquecimentos`.

---

## Configurando o n8n

Acesse `http://localhost:5678` (usuário: `admin` / senha: `admin`).

### Credenciais

Vá em **Settings → Credentials → Add Credential** e crie duas:

**Header Auth**
| Campo | Valor |
|---|---|
| Name | Header Auth account |
| Header Name | Authorization |
| Header Value | Bearer driva_test_key_abc123xyz789 |

**Postgres**
| Campo | Valor |
|---|---|
| Name | Postgres account |
| Host | postgres |
| Database | dados |
| User | admin |
| Password | admin |
| Port | 5432 |

### Importando os Workflows

Vá em **Workflows → Import from File** e importe nesta ordem:

1. `workflows/Data_Injestion.json`
2. `workflows/Cleaning.json`
3. `workflows/Processing.json`
4. `workflows/Scheduler.json`

Ative os quatro workflows com o toggle no canto superior direito de cada um.

> **Atenção:** Após importar, abra o **Scheduler** e reconecte os nós `Execute Data Injestion` e `Execute Cleaning` apontando para os workflows corretos importados, pois os IDs são gerados pelo n8n no momento da importação.

### Testando manualmente

Abra o workflow **Scheduler** e clique em **Execute Workflow**. Após a execução, verifique os dados:

```bash
docker exec -it postgres psql -U admin -d dados \
  -c "SELECT COUNT(*) FROM bronze_enrichments;"

docker exec -it postgres psql -U admin -d dados \
  -c "SELECT COUNT(*) FROM silver_enrichments;"

docker exec -it postgres psql -U admin -d dados \
  -c "SELECT COUNT(*) FROM gold_enriquecimentos;"
```

---

## Dashboard

Abra o arquivo `dashboard/dashboard.html` diretamente no navegador. Ele consome a API Analytics em `http://localhost:3001` e exibe:

- KPIs: total de jobs, taxa de sucesso, tempo médio
- Gráfico de jobs por status
- Tabela de enrichments com filtro por workspace e status
- Ranking de top workspaces

---

## Endpoints da API

### API Fonte — `http://localhost:3000`

```bash
# Lista enrichments paginados (simula dados com falhas propositais)
curl -H "Authorization: Bearer driva_test_key_abc123xyz789" \
  "http://localhost:3000/people/v1/enrichments?page=1&limit=50"
```

### API Analytics — `http://localhost:3001`

```bash
# Health check
curl http://localhost:3001/health

# KPIs gerais
curl http://localhost:3001/analytics/overview

# Jobs por status
curl http://localhost:3001/analytics/by-status

# Enrichments com filtros
curl "http://localhost:3001/analytics/enrichments?status_processamento=CONCLUIDO&limit=10"

# Top workspaces
curl http://localhost:3001/analytics/workspaces/top
```

---

## Troubleshooting

**Porta 5432 em uso**
```bash
sudo systemctl stop postgresql
docker compose up -d
```

**Tabelas não criadas após subir o banco**
```bash
docker compose down -v
docker volume rm postgres_data
docker compose up -d postgres
```

**Container em loop de restart**
```bash
docker compose logs <nome_do_container>
```
