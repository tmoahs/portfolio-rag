# Segmentation de clients e-commerce

## Contexte

Le projet de segmentation de clients e-commerce vise à regrouper les clients d'un site marchand en profils distincts, pour définir des actions marketing ciblées. La segmentation client est une application très courante du Machine Learning en entreprise : elle permet de comprendre les comportements et d'identifier des groupes partageant des caractéristiques communes, même sans données étiquetées. Ce projet introduit aussi l'usage de SQL pour l'analyse exploratoire, une compétence clé pour interroger des bases de données. Je l'ai réalisé dans le cadre de ma formation de Data Scientist OpenClassrooms, en 2025.

## Ce que j'ai fait (mon rôle personnel)

J'ai mené une analyse exploratoire des données directement en SQL, pour interroger la base de données clients. J'ai construit une analyse RFM (Récence, Fréquence, Montant) et une analyse en composantes principales (ACP) comme base de la segmentation. J'ai entraîné un modèle de clustering avec K-Means, complété par DBSCAN, pour regrouper les clients en segments. J'ai évalué la pertinence des clusters, puis analysé les segments pour en déduire des profils clients et proposer des actions marketing ciblées. J'ai aussi mené une analyse de stabilité (score ARI) sur 6 mois, et réfléchi à la maintenance et à la mise à jour du modèle de segmentation.

## Technologies utilisées

J'ai utilisé Python, SQL, Scikit-Learn, Pandas, NumPy, Matplotlib, Seaborn, les algorithmes K-Means et DBSCAN, ainsi que Jupyter Notebook.

## Résultats

L'analyse a permis d'identifier des profils distincts, par exemple 3 segments pour les nouveaux clients et 5 segments pour les clients fidèles. L'analyse de stabilité (score ARI) a validé la pertinence des segments sur 6 mois, ce qui a guidé la fréquence de réentraînement du modèle. Les segments ont été convertis en recommandations marketing ciblées. Le code est disponible sur github.com/tmoahs/Segmentation-Clients-Ecommerce.

## Ce que j'en ai appris

Ce projet m'a fait pratiquer le Machine Learning non supervisé et les algorithmes de clustering pour la segmentation client. J'y ai renforcé mon usage de SQL pour l'exploration de grands volumes de données. J'ai appris à évaluer la performance et la pertinence de modèles de clustering. Enfin, j'y ai travaillé la transformation d'une analyse technique en recommandations stratégiques et actionnables pour le marketing.
