-- 1. Ajout de la colonne is_test
ALTER TABLE exchanges ADD COLUMN IF NOT EXISTS is_test BOOLEAN DEFAULT FALSE;
ALTER TABLE feedbacks ADD COLUMN IF NOT EXISTS is_test BOOLEAN DEFAULT FALSE;

-- 2. Injection de 50 échanges fictifs
INSERT INTO exchanges (id, user_query, response_text, token_count, latency_seconds, top_distance, model_called, created_at, is_test)
SELECT
    gen_random_uuid(),
    -- Modifié légèrement avec modulo (i % 5) pour avoir des questions répétées (utile pour le top 3)
    'Quelle est la compétence ' || (i % 5) || ' de Thomas ?' AS user_query,
    CASE
        WHEN random() > 0.8 THEN 'Je ne dispose pas de cette information.'
        ELSE 'Thomas maîtrise parfaitement le sujet ' || i END AS response_text,
    floor(random() * 400 + 100)::int AS token_count,
    (random() * 2 + 0.5)::double precision AS latency_seconds,
    (random() * 0.6)::double precision AS top_distance,
    TRUE AS model_called,
    NOW() - (random() * (interval '7 days')) AS created_at,
    TRUE AS is_test
FROM generate_series(1, 50) s(i);

-- 3. Injection des feedbacks négatifs (avec -1)
INSERT INTO feedbacks (exchange_id, rating, comment)
SELECT id, -1, 'Pas assez précis'
FROM exchanges
WHERE is_test = TRUE
  AND random() > 0.7;
-------------------------------------------------------------------------------
-- REQUÊTE A : Statistiques quotidiennes consolidées (avec la moyenne glissante sur 7 jours)
WITH daily_metrics AS (
    SELECT
        DATE_TRUNC('day', e.created_at)::DATE AS stat_date,
        COUNT(e.id) AS total_questions,
        SUM(e.token_count) AS total_tokens,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY e.latency_seconds) AS median_latency,
        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY e.latency_seconds) AS p95_latency,

        COUNT(e.id) FILTER (
            WHERE e.response_text ILIKE '%ne dispose pas%'
               OR e.response_text ILIKE '%ne peux pas%'
        ) AS total_refusals,

        COUNT(f.exchange_id) FILTER (WHERE f.rating = -1) AS negative_feedbacks

    FROM exchanges e
    LEFT JOIN feedbacks f ON e.id = f.exchange_id
    WHERE e.is_test = TRUE -- TEMPORAIRE : TRUE pour tester
    GROUP BY DATE_TRUNC('day', e.created_at)::DATE
)
SELECT
    stat_date,
    total_questions,
    ROUND(AVG(total_questions) OVER (
        ORDER BY stat_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ), 1) AS moving_avg_7d,
    total_tokens,
    median_latency,
    p95_latency,
    ROUND((total_refusals::NUMERIC / NULLIF(total_questions, 0)) * 100, 2) AS refusal_rate,
    ROUND((negative_feedbacks::NUMERIC / NULLIF(total_questions, 0)) * 100, 2) AS negative_feedback_rate
FROM daily_metrics
ORDER BY stat_date DESC;

-- REQUÊTE B : Classement des questions les plus fréquentes
WITH question_counts AS (
    SELECT
        DATE_TRUNC('day', created_at)::DATE AS stat_date,
        user_query,
        COUNT(*) as q_count
    FROM exchanges
    WHERE is_test = TRUE -- TEMPORAIRE : TRUE pour tester
    GROUP BY 1, 2
)
SELECT
    stat_date,
    user_query,
    q_count,
    RANK() OVER (PARTITION BY stat_date ORDER BY q_count DESC) as daily_rank
FROM question_counts
WHERE daily_rank <= 3;

-- REQUÊTE C : La vue Dashboard (basée sur la table finale que ton DAG remplira)
-- Note : On retire "is_test" ici car cette vue servira en production
CREATE OR REPLACE VIEW v_dashboard_metrics AS
SELECT
    d.stat_date,
    d.total_questions,
    d.median_latency,
    d.refusal_rate,
    d.negative_feedback_rate,
    AVG(d.total_questions) OVER (
        ORDER BY d.stat_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS volume_trend_7d
FROM daily_stats d
ORDER BY d.stat_date DESC;

-- REQUÊTE D : Test de performance sur les mauvaises recherches
EXPLAIN ANALYZE
SELECT e.id, e.user_query, 'DISTANCE_ELEVEE' AS flag_reason
FROM exchanges e
WHERE e.top_distance > 0.40
  AND e.is_test = TRUE;
------------------------------------------------------------------------------------------------------
-- 1. Table des statistiques quotidiennes
CREATE TABLE IF NOT EXISTS daily_stats (
    stat_date DATE PRIMARY KEY,
    total_questions INT DEFAULT 0,
    total_tokens INT DEFAULT 0,
    median_latency NUMERIC(5,2),
    p95_latency NUMERIC(5,2),
    refusal_rate NUMERIC(5,2),
    negative_feedback_rate NUMERIC(5,2)
);

-- 2. Table des questions problématiques (avec UUID pour correspondre à ta table exchanges)
CREATE TABLE IF NOT EXISTS flagged_questions (
    exchange_id UUID PRIMARY KEY,
    question TEXT NOT NULL,
    flag_reason VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Table des logs du pipeline (au cas où elle ne serait pas créée par le DAG)
CREATE TABLE IF NOT EXISTS pipeline_logs (
    run_id VARCHAR PRIMARY KEY,
    dag_id VARCHAR,
    execution_date DATE,
    status VARCHAR,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-----------
SELECT * FROM daily_stats;
SELECT * FROM flagged_questions;