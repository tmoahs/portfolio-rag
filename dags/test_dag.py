from datetime import timedelta
from datetime import datetime
from airflow.sdk import DAG
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.decorators import dag, task


@dag(start_date=datetime(2024, 1, 1), schedule=None, catchup=False)
def mon_dag_de_test():
    @task
    def debut():
        return 'Début du test'

    @task(retries=1, retry_delay=timedelta(seconds=30))
    def tache1(result):
        print(f"Message reçu : {result}")
        raise ValueError('Échec provoqué')

    tache1(debut())


mon_dag_de_test()