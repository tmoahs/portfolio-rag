# Pipeline Big Data AgriTech · AWS EMR et Spark

## Contexte

Le projet Pipeline Big Data AgriTech s'inscrit dans un scénario d'entreprise : une start-up AgriTech développe des robots cueilleurs intelligents, et sa première brique est une application mobile qui identifie un fruit à partir d'une photo. Les images collectées serviront à entraîner le futur moteur de classification, et leur volume va augmenter très rapidement. Le vrai enjeu n'était donc pas de coder un modèle, mais de bâtir une chaîne de traitement capable de passer de quelques milliers à plusieurs millions d'images sans être refaite de zéro. J'ai réalisé ce projet dans le cadre de ma formation de Data Scientist OpenClassrooms, en 2025.

## Ce que j'ai fait (mon rôle personnel)

J'ai conçu l'architecture avant de coder, dans une logique « cloud-native » de bout en bout : lecture des images brutes depuis Amazon S3, traitement sur un cluster AWS EMR, puis réécriture sur S3, sans stockage intermédiaire local. J'ai mis en place un pipeline PySpark et utilisé le transfer learning avec MobileNetV2, un réseau déjà entraîné, pour transformer chaque photo en vecteur de caractéristiques. J'ai optimisé le traitement en utilisant le broadcast, qui diffuse les poids du modèle une seule fois vers tous les nœuds au lieu de les recharger sur chaque worker. J'ai parallélisé l'inférence image via des Pandas UDF, puis réduit la dimension des features de 1280 à 100 composantes avec une PCA sous PySpark ML. J'ai stocké les résultats au format Parquet sur S3, et rédigé une analyse critique des coûts et des performances avec des recommandations pour la mise en production (Auto Scaling, instances Spot, monitoring). J'ai aussi configuré les serveurs S3 et EMR en Europe pour respecter le RGPD.

## Technologies utilisées

J'ai utilisé AWS EMR et Amazon S3, PySpark et PySpark ML, les Pandas UDF, le modèle MobileNetV2, TensorFlow et Keras, le format Parquet, Pillow, Pandas et NumPy.

## Résultats

Le pipeline scalable suit un enchaînement S3 → EMR → S3, sans stockage local. La réduction de dimension par PCA fait passer les features de 1280 à 100 composantes. Les serveurs sont localisés en Europe, ce qui assure la conformité RGPD. Le pipeline ne dépend pas de la taille des données : passer de 10 000 à 10 millions d'images se traduit par l'ajout de nœuds au cluster. Le code est disponible sur github.com/tmoahs/Traitement-Big-Data.

## Difficultés rencontrées et solutions

Sur le pipeline Big Data AgriTech, un premier obstacle venait du fonctionnement distribué : sur un cluster, chaque nœud exécute ses tâches en parallèle, et sans précaution chaque worker rechargeait le réseau de neurones, ce qui gaspillait mémoire et temps. Je l'ai résolu en diffusant les poids de MobileNetV2 une seule fois vers tous les nœuds grâce au broadcast. Le traitement des images en boucle aurait été trop lent : je l'ai parallélisé avec des Pandas UDF exécutées sur l'ensemble du cluster. Enfin, stocker les vecteurs dans leurs 1280 dimensions initiales aurait été coûteux ; une PCA sous PySpark ML les a ramenés à 100 composantes, ce qui a fortement réduit le volume à stocker et à lire.

## Ce que j'en ai appris

J'ai retenu qu'en Spark, deux détails changent tout : le broadcast et les Pandas UDF. Sans eux, on paie le coût de transfert du modèle sur chaque nœud et on perd le bénéfice du parallélisme. J'ai aussi appris que réduire la dimension sert à maîtriser le stockage : passer de 1280 à 100 composantes divise par plus de dix le volume stocké et lu, avec un gain direct sur le coût cloud. Enfin, j'ai compris que le coût et la conformité font partie de la conception, car la région des serveurs ou l'usage d'instances Spot se décident au moment de l'architecture.
