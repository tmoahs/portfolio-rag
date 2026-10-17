TEST_CASES = [
    # Parcours & Formation
    {"question": "Quelles sont les expériences professionnelles de Thomas Patout ?", "expected_source": "parcours.md"},
    {"question": "Quel est son niveau d'anglais et son score au TOEIC ?", "expected_source": "formation.md"},

    # Compétences & Recherche
    {"question": "Quelles compétences utilise-t-il en production ?", "expected_source": "competences.md"},
    {"question": "Quel type de contrat et de poste recherche-t-il ?", "expected_source": "recherche-emploi.md"},

    # Projets ciblés
    {"question": "Comment le modèle de scoring de crédit est-il déployé ?",
     "expected_source": "projet-scoring-credit.md"},
    {"question": "Comment le coût est-il maintenu à zéro sur Events Curator ?",
     "expected_source": "projet-events-curator.md"},
    {"question": "Quelle architecture a-t-il mise en place sur le projet AgriTech ?",
     "expected_source": "projet-pipeline-big-data-agritech.md"},
    {"question": "Quel rôle a-t-il tenu dans le projet de cadrage IA ?",
     "expected_source": "projet-cadrage-pilotage-ia.md"},
    {"question": "Comment a-t-il traité les valeurs manquantes sur Open Food Facts ?",
     "expected_source": "projet-preparation-donnees-sante-publique.md"},
    {"question": "Quel est le résultat du projet de prédiction de consommation de bâtiments ?",
     "expected_source": "projet-prediction-consommation-batiments.md"},

    # Pièges (questions hors base / hors sujet)
    {"question": "Quelle est son expérience de développement avec le langage Rust ou C++ ?", "expected_source": None},
    {"question": "Quelle est la météo aujourd'hui à Tours ?", "expected_source": None},
    {"question": "Combien d'années a-t-il travaillé chez Google comme lead developer ?", "expected_source": None},
]