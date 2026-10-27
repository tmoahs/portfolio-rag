from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# 1. Calcul des statistiques globales avec filet de sécurité (NULLIF) pour les jours à 0 question
sql_compute_stats = """
    INSERT INTO daily_stats (stat_date, total_questions, total_tokens, median_latency, p95_latency, refusal_rate, negative_feedback_rate)
    WITH daily_metrics AS (
        SELECT
            DATE_TRUNC('day', e.created_at)::DATE AS stat_date,
            COUNT(e.id) AS total_questions,
            SUM(e.token_count) AS total_tokens,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY e.latency_seconds)
                FILTER (WHERE e.model_called) AS median_latency,
            PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY e.latency_seconds)
                FILTER (WHERE e.model_called) AS p95_latency,
            COUNT(e.id) FILTER (
                WHERE e.response_text ILIKE '%ne dispose pas%'
                   OR e.response_text ILIKE '%ne peux pas%'
                   OR e.response_text ILIKE '%ne peux donc pas%'
                   OR e.response_text ILIKE '%je suis dédié%'
                   OR e.response_text ILIKE '%hors de mon périmètre%'
            ) AS total_refusals,
            COUNT(f.exchange_id) FILTER (WHERE f.rating = -1) AS negative_feedbacks
        FROM exchanges e
        LEFT JOIN feedbacks f ON e.id = f.exchange_id
        WHERE e.is_test = FALSE
          AND DATE_TRUNC('day', e.created_at)::DATE = '{{ ds }}'::DATE
        GROUP BY DATE_TRUNC('day', e.created_at)::DATE
    )
    SELECT
        stat_date,
        total_questions,
        total_tokens,
        median_latency,
        p95_latency,
        ROUND((total_refusals::NUMERIC / NULLIF(total_questions, 0)) * 100, 2) AS refusal_rate,
        ROUND((negative_feedbacks::NUMERIC / NULLIF(total_questions, 0)) * 100, 2) AS negative_feedback_rate
    FROM daily_metrics
    ON CONFLICT (stat_date) DO UPDATE SET
        total_questions = EXCLUDED.total_questions,
        total_tokens = EXCLUDED.total_tokens,
        median_latency = EXCLUDED.median_latency,
        p95_latency = EXCLUDED.p95_latency,
        refusal_rate = EXCLUDED.refusal_rate,
        negative_feedback_rate = EXCLUDED.negative_feedback_rate;
"""

# 2. Identification des questions problématiques
sql_flag_questions = """
    INSERT INTO flagged_questions (exchange_id, question, flag_reason, created_at)
    SELECT 
        e.id, 
        e.user_query, 
        CASE 
            WHEN f.rating = -1 THEN 'FEEDBACK_NEGATIF'
            WHEN e.top_distance > 0.40 THEN 'DISTANCE_ELEVEE'
            ELSE 'REFUS' 
        END AS flag_reason,
        e.created_at
    FROM exchanges e
    LEFT JOIN feedbacks f ON e.id = f.exchange_id
    WHERE e.is_test = FALSE
      AND DATE_TRUNC('day', e.created_at)::DATE = '{{ ds }}'::DATE
      AND (
          f.rating = -1 
          OR e.top_distance > 0.40 
          OR e.response_text ILIKE '%ne dispose pas%' 
          OR e.response_text ILIKE '%ne peux pas%'
          OR e.response_text ILIKE '%ne peux donc pas%'
          OR e.response_text ILIKE '%je suis dédié%'
          OR e.response_text ILIKE '%hors de mon périmètre%'
      )
    ON CONFLICT (exchange_id) DO UPDATE SET 
        flag_reason = EXCLUDED.flag_reason;
"""

# 3. Usage des chunks : quelles sources servent vraiment ?
# Recalcul complet et idempotent (pas de double comptage si le DAG est relancé).
sql_chunk_usage = """
    CREATE TABLE IF NOT EXISTS chunk_usage (
        chunk_id VARCHAR(255) PRIMARY KEY,
        retrieval_count INT DEFAULT 0,
        last_retrieved_at TIMESTAMP
    );

    INSERT INTO chunk_usage (chunk_id, retrieval_count, last_retrieved_at)
    SELECT rc.chunk_id, COUNT(*)::INT, MAX(e.created_at)
    FROM retrieved_chunks rc
    JOIN exchanges e ON e.id = rc.exchange_id
    WHERE e.is_test = FALSE
    GROUP BY rc.chunk_id
    ON CONFLICT (chunk_id) DO UPDATE SET
        retrieval_count = EXCLUDED.retrieval_count,
        last_retrieved_at = EXCLUDED.last_retrieved_at;
"""

# 4. Traçabilité du run dans une table de logs
sql_log_run = """
    CREATE TABLE IF NOT EXISTS pipeline_logs (
        run_id VARCHAR PRIMARY KEY,
        dag_id VARCHAR,
        execution_date DATE,
        status VARCHAR,
        completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    INSERT INTO pipeline_logs (run_id, dag_id, execution_date, status)
    VALUES ('{{ run_id }}', '{{ dag.dag_id }}', '{{ ds }}'::DATE, 'SUCCESS')
    ON CONFLICT (run_id) DO NOTHING;
"""

with DAG(
    'analytics_daily_compute',
    default_args=default_args,
    description='Calcule les métriques RAG et isole les lacunes',
    schedule='0 2 * * *', # Tourne à 2h00 du matin
    start_date=datetime(2023, 1, 1),
    catchup=False, # Pas de rattrapage incontrôlé
    max_active_runs=1, # Une seule exécution à la fois
    tags=['rag', 'analytics'],
) as dag:

    compute_stats = SQLExecuteQueryOperator(
        task_id='compute_daily_stats',
        conn_id='postgres_default',
        sql=sql_compute_stats,
    )

    flag_questions = SQLExecuteQueryOperator(
        task_id='flag_questions',
        conn_id='postgres_default',
        sql=sql_flag_questions,
    )

    compute_chunk_usage = SQLExecuteQueryOperator(
        task_id='compute_chunk_usage',
        conn_id='postgres_default',
        sql=sql_chunk_usage,
    )

    log_run = SQLExecuteQueryOperator(
        task_id='log_run',
        conn_id='postgres_default',
        sql=sql_log_run,
    )

    # Ordre d'exécution
    compute_stats >> flag_questions >> compute_chunk_usage >> log_run