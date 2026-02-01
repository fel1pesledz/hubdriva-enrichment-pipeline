CREATE TABLE bronze_enrichments (
  id UUID PRIMARY KEY,
  id_workspace UUID,
  workspace_name TEXT,
  total_contacts INTEGER,
  contact_type TEXT,
  status TEXT,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

CREATE TABLE gold_enriquecimentos (
  id_enriquecimento UUID PRIMARY KEY,
  id_workspace UUID,
  nome_workspace TEXT,
  total_contatos INTEGER,
  tipo_contato TEXT,
  status_processamento TEXT,
  data_criacao TIMESTAMP,
  data_atualizacao TIMESTAMP,

  duracao_processamento_minutos NUMERIC,
  tempo_por_contato_minutos NUMERIC,
  processamento_sucesso BOOLEAN,
  categoria_tamanho_job TEXT,
  necessita_reprocessamento BOOLEAN,

  data_atualizacao_dw TIMESTAMP
);
