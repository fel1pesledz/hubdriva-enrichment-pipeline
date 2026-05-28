-- Tabela Bronze: dados brutos da API
CREATE TABLE IF NOT EXISTS bronze_enrichments (
    id                VARCHAR PRIMARY KEY,
    id_workspace      VARCHAR,
    workspace_name    VARCHAR,
    total_contacts    INTEGER,
    contact_type      VARCHAR,
    status            VARCHAR,
    created_at        TIMESTAMP,
    updated_at        TIMESTAMP
);

-- Tabela Cleaning: dados limpos e padronizados
CREATE TABLE IF NOT EXISTS silver_enrichments (
    id                              VARCHAR PRIMARY KEY,
    id_workspace                    VARCHAR,
    workspace_name                  VARCHAR,
    total_contacts                  INTEGER,
    contact_type                    VARCHAR,
    status                          VARCHAR,
    created_at                      TIMESTAMP,
    updated_at                      TIMESTAMP,
    -- campos de qualidade
    registro_valido                 BOOLEAN,
    motivo_invalido                 VARCHAR,
    ingestao_at                     TIMESTAMP
);

-- Tabela Gold: dados transformados e enriquecidos
CREATE TABLE IF NOT EXISTS gold_enriquecimentos (
    id_enriquecimento               VARCHAR PRIMARY KEY,
    id_workspace                    VARCHAR,
    nome_workspace                  VARCHAR,
    total_contatos                  INTEGER,
    tipo_contato                    VARCHAR,
    status_processamento            VARCHAR,
    data_criacao                    TIMESTAMP,
    data_atualizacao                TIMESTAMP,
    duracao_processamento_minutos   NUMERIC,
    tempo_por_contato_minutos       NUMERIC,
    processamento_sucesso           BOOLEAN,
    categoria_tamanho_job           VARCHAR,
    necessita_reprocessamento       BOOLEAN,
    data_atualizacao_dw             TIMESTAMP
);

