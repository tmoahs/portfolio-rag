-- Création de la table principale des échanges
CREATE TABLE IF NOT EXISTS exchanges (
    id UUID PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    user_query TEXT NOT NULL,
    rewritten_query TEXT,
    response_text TEXT,
    latency_seconds FLOAT,
    token_count INTEGER,
    model_name VARCHAR(100),
    top_distance FLOAT,
    model_called BOOLEAN NOT NULL DEFAULT TRUE,
    config_version VARCHAR(50)
);

-- Création de la table des chunks récupérés par le retriever
CREATE TABLE IF NOT EXISTS retrieved_chunks (
    id BIGSERIAL PRIMARY KEY,
    exchange_id UUID NOT NULL REFERENCES exchanges(id) ON DELETE CASCADE,
    chunk_id VARCHAR(100) NOT NULL,
    rank SMALLINT NOT NULL,
    distance FLOAT NOT NULL,
    used_in_response BOOLEAN NOT NULL DEFAULT TRUE
);

-- Création de la table des retours utilisateurs
CREATE TABLE IF NOT EXISTS feedbacks (
    id BIGSERIAL PRIMARY KEY,
    exchange_id UUID NOT NULL UNIQUE REFERENCES exchanges(id) ON DELETE CASCADE,
    rating SMALLINT NOT NULL,
    comment TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index pour optimiser les requêtes analytiques et les jointures
CREATE INDEX IF NOT EXISTS idx_exchanges_created_at ON exchanges(created_at);
CREATE INDEX IF NOT EXISTS idx_chunks_exchange_id ON retrieved_chunks(exchange_id);
CREATE INDEX IF NOT EXISTS idx_feedbacks_exchange_id ON feedbacks(exchange_id);