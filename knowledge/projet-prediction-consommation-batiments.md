# Prédiction de la consommation énergétique de bâtiments

## Contexte

Le projet de prédiction de la consommation énergétique de bâtiments vise à anticiper la consommation et les émissions de CO2 de bâtiments, afin de cibler les rénovations les plus rentables. Il s'inscrit dans le workflow complet d'un projet de Machine Learning supervisé, l'application la plus courante en entreprise. Un accent particulier est mis sur l'explicabilité des modèles (XAI), pour garantir la transparence et la confiance dans les prédictions. J'ai réalisé ce projet dans le cadre de ma formation de Data Scientist OpenClassrooms, en 2025.

## Ce que j'ai fait (mon rôle personnel)

J'ai créé de nouvelles variables à partir des données brutes, dans un travail important de feature engineering destiné à améliorer la performance et la pertinence du modèle. J'ai entraîné et évalué plusieurs algorithmes de Machine Learning supervisé avec la librairie Scikit-Learn. J'ai optimisé le modèle final, un LightGBM, pour obtenir les meilleures prédictions possibles. J'ai ensuite analysé l'explicabilité du modèle avec SHAP, afin de comprendre comment les variables influencent les prédictions et d'identifier les principaux leviers d'optimisation énergétique.

## Technologies utilisées

J'ai utilisé Python, Scikit-Learn, LightGBM, SHAP, Pandas, NumPy, Matplotlib, Seaborn et Jupyter Notebook.

## Résultats

Le modèle de régression LightGBM atteint un R² de 0,85 après le travail de feature engineering. L'analyse SHAP a permis d'identifier les principaux leviers d'optimisation énergétique des bâtiments. Le code est disponible sur github.com/tmoahs/Prediction-Consommation-Batiments.

## Ce que j'en ai appris

Ce projet m'a fait pratiquer le feature engineering, c'est-à-dire la création de variables pertinentes à partir de données brutes pour alimenter un modèle. J'y ai maîtrisé le workflow complet du Machine Learning supervisé : sélection, entraînement et évaluation de modèles prédictifs. J'y ai aussi développé ma capacité à expliquer le fonctionnement d'un modèle « boîte noire » et à justifier ses prédictions grâce à l'interprétabilité (XAI).
