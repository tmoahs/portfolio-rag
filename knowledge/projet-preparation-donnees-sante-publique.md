# Préparation de données de santé publique

## Contexte

Le projet de préparation de données de santé publique simule une situation réelle où un Data Scientist doit plonger dans un nouveau jeu de données, identifier ses défauts et le transformer en une base solide pour la prise de décision. Le jeu de données utilisé est Open Food Facts, et l'objectif est d'évaluer la faisabilité d'un système d'auto-complétion des informations nutritionnelles. Comme la qualité des analyses et des modèles dépend entièrement de la qualité des données en entrée, le projet porte sur le nettoyage et la préparation des données. Je l'ai réalisé dans le cadre de ma formation de Data Scientist OpenClassrooms, en 2025.

## Ce que j'ai fait (mon rôle personnel)

J'ai nettoyé le jeu de données Open Food Facts en identifiant et en traitant les incohérences, les erreurs et les valeurs manquantes. J'ai traité les outliers de manière avancée et imputé les valeurs manquantes avec la méthode KNN Imputer. J'ai mené une analyse exploratoire approfondie, avec des analyses univariées et multivariées pour comprendre les relations entre les variables. J'ai créé des visualisations de données avancées pour illustrer les insights et justifier mes choix de nettoyage et d'analyse. J'ai réalisé une ACP et une ANOVA, et décomposé le problème métier en une série de tâches d'analyse avec des hypothèses pour guider la préparation des données.

## Technologies utilisées

J'ai utilisé Python, Pandas, NumPy, Matplotlib, Seaborn, l'imputation KNN, l'analyse en composantes principales (ACP), l'ANOVA et Jupyter Notebook.

## Résultats

Les analyses statistiques, notamment l'ANOVA, ont validé que des catégories clés comme le Nutri-Score expliquent significativement la composition des produits, ce qui confirme la viabilité du système d'auto-complétion. Le jeu de données a été nettoyé et préparé pour servir de base à la prise de décision. Le code est disponible sur github.com/tmoahs/Preparation-Donnees-Sante-Publique.

## Ce que j'en ai appris

Ce projet m'a fait travailler le nettoyage de données : traitement des incohérences, des doublons et des valeurs manquantes. J'y ai réalisé des analyses statistiques univariées et multivariées pour explorer les relations entre variables. J'ai développé ma data visualisation avancée, en utilisant des graphiques pertinents pour appuyer une analyse et communiquer des résultats. Enfin, j'y ai appris à décomposer un problème business en tâches analytiques et à justifier mes décisions sur la base des données.
