from datetime import timedelta
from datetime import datetime
from airflow.sdk import DAG
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.decorators import dag, task


@dag(start_date=datetime(2024, 1, 1), schedule=None, catchup=False)
def test_rag():
    @task
    def tache1():
        import os
        from src.rag.config import KNOWLEDGE_DIR
        fichiers = os.listdir(KNOWLEDGE_DIR)
        print(f"Nombre de fichiers dans {KNOWLEDGE_DIR} : {len(fichiers)}")

    tache1()


test_rag()