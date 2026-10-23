import os
import pytest
from airflow.models import DagBag


def test_no_import_errors():
    """
    Vérifie que tous les DAGs dans le dossier /dags se chargent sans erreur de syntaxe ou d'import.
    """

    dags_folder = os.path.join(os.path.dirname(__file__), "..", "dags")
    dag_bag = DagBag(dag_folder=dags_folder, include_examples=False)

    assert len(dag_bag.import_errors) == 0, f"Erreurs d'import trouvées : {dag_bag.import_errors}"