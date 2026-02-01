
# HubDriva – Data Enrichment Monitoring

Esta solução foi projetada para monitorar a performance e a qualidade dos enriquecimentos de dados da plataforma HubDriva.  
Ela consiste em uma pipeline automatizada que transforma dados brutos em insights analíticos consumidos por um dashboard.

---

## Ambiente Docker

O ambiente é totalmente containerizado, garantindo portabilidade, reprodutibilidade e isolamento entre os serviços.

### Containers incluídos

- PostgreSQL – Data Warehouse
- n8n – Orquestração da pipeline
- API – Fonte de dados e camada de analytics
- Frontend (Dashboard) – Visualização dos KPIs

---

## Pipeline de Dados (n8n)

Um fluxo orquestrado no n8n executa a cada 5 minutos, realizando:

1. Ingestão: API → Camada Bronze  
2. Processamento: Bronze → Camada Gold

---

## Camadas do Data Warehouse

### Bronze

- Armazena os registros brutos
- Contém carimbos de data de ingestão e atualização
- Não possui transformações de negócio

### Gold

- Dados limpos e normalizados
- Campos traduzidos para português
- Enriquecidos com métricas de performance e sucesso

---

## Subindo o Ambiente

### Build dos containers

O build deve ser executado na pasta raiz do projeto, onde está localizado o arquivo `docker-compose.yml`.

```bash
docker compose build
Subir os containers
docker compose up -d
Verificar se todos os serviços estão rodando
docker ps
Certifique-se de que todos os containers (PostgreSQL, n8n, API e Dashboard) estejam com o status Up.
Caso algum container não esteja rodando, verifique os logs:

docker logs <nome_do_container>
Subindo o Frontend (Dashboard)
Para rodar o servidor do frontend, você precisa estar dentro da pasta dashboard.

cd dashboard
python -m http.server 8000
Acesse no navegador:

http://localhost:8000
Importação dos Workflows no n8n
Acesse a interface do n8n:

http://localhost:5678
Passos
No menu lateral, clique em Workflows

Selecione Import from File

Importe os arquivos JSON do repositório

Workflows obrigatórios
Data Ingestion

Processing

Scheduler

Configuração Inicial
Antes de executar os workflows, verifique:

As credenciais do PostgreSQL configuradas corretamente nos nós do n8n

A URL da API configurada como:

http://api:3000
Header de autenticação:

Authorization: Bearer driva_test_key_abc123xyz789
Execução dos Workflows
Execução manual
Para testar manualmente:

Abra o workflow desejado no n8n

Clique em Execute Workflow

Fluxo executado:

API → Bronze → Gold
Endpoints da API
Endpoint de Fonte (Ingestão)
Simula a API de enriquecimentos consumida pelo n8n para popular a camada Bronze.

curl -X GET "http://localhost:3000/people/v1/enrichments?page=1&limit=50" \
  -H "Authorization: Bearer driva_test_key_abc123xyz789"
Analytics Overview (KPIs)
Retorna métricas consolidadas da camada Gold:

Total de jobs

Taxa de sucesso

Tempo médio de processamento

curl -X GET "http://localhost:3000/analytics/overview" \
  -H "Authorization: Bearer driva_test_key_abc123xyz789"
