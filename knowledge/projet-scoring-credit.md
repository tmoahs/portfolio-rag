# Scoring de crédit · API, Monitoring et Dashboard

## Contexte

Le projet de scoring de crédit part d'un besoin métier simple : une institution financière doit décider d'accorder ou non un crédit à un client. Deux erreurs sont possibles et elles n'ont pas le même coût : refuser un bon client fait perdre une marge, tandis qu'accepter un mauvais payeur fait perdre le capital prêté. Un modèle classique optimisé sur l'accuracy ou sur l'AUC seule traite ces deux erreurs comme équivalentes, ce qui ne correspond pas au besoin de l'entreprise. La vraie question était donc : quel modèle coûte le moins cher ? J'ai réalisé ce projet dans le cadre de ma formation de Data Scientist OpenClassrooms, en 2025.

## Ce que j'ai fait (mon rôle personnel)

J'ai mené l'analyse exploratoire et le feature engineering, en gérant un fort déséquilibre de classes entre bons et mauvais payeurs. J'ai stocké les variables préparées dans une base SQLite qui sert de feature store commun à l'API et au dashboard. J'ai comparé plusieurs algorithmes sur les mêmes données, puis sélectionné un LightGBM pour son rapport entre performance, temps d'entraînement et interprétabilité. J'ai défini un score métier, une fonction de coût qui pondère différemment un faux positif et un faux négatif, puis j'ai optimisé le seuil de décision sur ce coût au lieu de le fixer à 0,5 par défaut. J'ai calculé des valeurs SHAP locales et globales pour rendre chaque décision explicable. J'ai déployé une API FastAPI conteneurisée avec Docker, des tests automatisés et un pipeline CI/CD, ainsi qu'un dashboard Streamlit qui consomme cette API. J'ai aussi assuré le suivi des expériences avec MLflow et la génération d'un rapport de dérive avec Evidently AI, et j'ai ajouté une page d'accueil et un endpoint `/health` sur l'API.

## Technologies utilisées

J'ai utilisé Python, LightGBM, FastAPI, Docker, CI/CD (workflow GitHub Actions), MLflow, Streamlit, SHAP, Evidently AI, SQLite et Pandas.

## Résultats

Le modèle LGBM atteint un AUC de 0,79 sur les données de test. Le projet couvre 100 % du cycle : données, modèle, API et dashboard. Deux applications sont déployées et accessibles en ligne : l'API FastAPI et le dashboard Streamlit. Pour chaque dossier, le chargé de clientèle voit quels facteurs ont pesé dans la décision, ce qui rend un refus défendable et répond aux exigences de transparence sur les décisions automatisées. Le dashboard est accessible à l'adresse scoring-api-p8.streamlit.app, et le code est disponible sur github.com/tmoahs/Scoring-Credit-API.

## Difficultés rencontrées et solutions

Sur le projet de scoring de crédit, un premier point difficile a été de gérer un fort déséquilibre de classes entre bons et mauvais payeurs, que j'ai traité par la préparation des données et le feature engineering. La matrice de coûts qui définit le score métier restait une hypothèse : en conditions réelles, elle devrait être co-construite et validée par les équipes risque, car elle relève d'un dialogue entre le métier et la technique. Enfin, la page d'accueil de l'API ne renvoyait qu'un JSON sans intérêt pour un visiteur ; je l'ai remplacée par une page HTML qui oriente vers la documentation Swagger et le dashboard, et j'ai ajouté un endpoint `/health` pour que l'état du service et du modèle puisse être vérifié automatiquement.

## Ce que j'en ai appris

J'ai retenu qu'un modèle se juge sur son coût métier : deux modèles avec la même AUC peuvent avoir des conséquences financières très différentes selon l'endroit où l'on place le seuil, et c'est donc le seuil qu'il faut optimiser en priorité. J'ai aussi appris qu'un modèle n'a de valeur que s'il est utilisable par ceux qui décident, d'où le dashboard pensé pour des non-techniciens plutôt qu'une API réservée à des data scientists. Enfin, j'ai compris que le monitoring fait partie du travail : les données de production dérivent, et sans rapport de dérive on découvre le problème trop tard.
