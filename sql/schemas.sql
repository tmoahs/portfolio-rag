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
    config_version VARCHAR(50),
    -- Permet de séparer les échanges de test des vraies statistiques.
    is_test BOOLEAN NOT NULL DEFAULT FALSE
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

-- Préparation de la table PostgreSQL
CREATE TABLE IF NOT EXISTS documents_state (
    filename VARCHAR(255) PRIMARY KEY,
    file_hash VARCHAR(64) NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

----------------------------------------------------------
-- 1. Table des statistiques quotidiennes (Une ligne par jour)
CREATE TABLE IF NOT EXISTS daily_stats (
    stat_date DATE PRIMARY KEY,
    total_questions INT DEFAULT 0,
    median_latency NUMERIC(5,2),
    p95_latency NUMERIC(5,2),
    total_tokens INT DEFAULT 0,
    negative_feedback_rate NUMERIC(5,2), -- Pourcentage
    refusal_rate NUMERIC(5,2)            -- Pourcentage
);

-- 2. Table des questions à examiner (Lacunes, refus, mauvais retours)
CREATE TABLE IF NOT EXISTS flagged_questions (
    exchange_id VARCHAR(36) PRIMARY KEY,
    question TEXT NOT NULL,
    flag_reason VARCHAR(50) NOT NULL, -- Ex: 'FEEDBACK_NEGATIF', 'DISTANCE_ELEVEE', 'REFUS'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Table d'usage des chunks (Efficacité des sources)
CREATE TABLE IF NOT EXISTS chunk_usage (
    chunk_id VARCHAR(255) PRIMARY KEY,
    retrieval_count INT DEFAULT 0,
    last_retrieved_at TIMESTAMP
);

-- 4. Traçabilité des exécutions des DAGs (une ligne par run)
CREATE TABLE IF NOT EXISTS pipeline_logs (
    run_id VARCHAR PRIMARY KEY,
    dag_id VARCHAR,
    execution_date DATE,
    status VARCHAR,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Cache de réponses (exact + sémantique), versionné par corpus/modèles/prompt
CREATE TABLE IF NOT EXISTS answer_cache (
    id BIGSERIAL PRIMARY KEY,
    cache_version VARCHAR(64) NOT NULL,
    question_norm TEXT NOT NULL,
    question_text TEXT NOT NULL,
    embedding JSONB,
    answer TEXT NOT NULL,
    sources JSONB NOT NULL DEFAULT '[]',
    chunks JSONB NOT NULL DEFAULT '[]',
    hits INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_hit_at TIMESTAMPTZ,
    UNIQUE (cache_version, question_norm)
);

CREATE INDEX IF NOT EXISTS idx_answer_cache_created_at ON answer_cache(created_at);

