# Classification multimodale de produits

## Contexte

Le projet de classification multimodale de produits vise à classer automatiquement des biens de consommation en exploitant deux types de données : leurs descriptions textuelles (NLP) et leurs images (vision par ordinateur). La capacité à modéliser des données non structurées comme le texte ou les images est une compétence recherchée, menant à des postes spécialisés en NLP ou en Computer Vision. Ce projet avait donc pour but de développer une expertise sur ces deux types de données, dans le cadre de ma formation de Data Scientist OpenClassrooms, en 2025.

## Ce que j'ai fait (mon rôle personnel)

J'ai prétraité les données textuelles (descriptions produits) en appliquant des techniques de nettoyage et de tokenisation. J'ai prétraité les données images en les redimensionnant et en leur appliquant des techniques d'analyse. J'ai appliqué des techniques de feature engineering adaptées au texte (TF-IDF) et aux images (SIFT). J'ai entraîné et comparé des modèles de Machine Learning supervisés et non supervisés pour classer les produits. L'approche a été validée par des modèles de Deep Learning : BERT pour le texte et CNN pour les images. J'ai aussi été initié à l'utilisation d'API en Python dans le cadre du projet.

## Technologies utilisées

J'ai utilisé Python, Scikit-Learn, Pandas, NLTK, Pillow, OpenCV, TensorFlow/Keras, BERT, TF-IDF, SIFT et Jupyter Notebook.

## Résultats

Le modèle final est un CNN entraîné sur les images, qui atteint une accuracy de 81,3 %, soit environ 80 %. L'approche texte (NLP) a été validée séparément avec BERT, et j'ai conclu que combiner le texte et l'image donnerait de meilleurs résultats, sans que cette combinaison soit retenue pour le modèle final. Le code est disponible sur github.com/tmoahs/Classification-Produits-NLP-Vision.

## Ce que j'en ai appris

Ce projet m'a fait acquérir les étapes de prétraitement et de feature engineering pour les données textuelles (NLP). J'y ai appliqué des techniques de traitement et d'analyse sur des données images (Computer Vision). J'ai appris à entraîner des modèles adaptés à des données non structurées, texte comme image. Je me suis également initié à l'intégration de services externes via des API en Python.
