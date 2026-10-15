# Veille et POC · Few-Shot Learning (SetFit)

## Contexte

La veille et le POC Few-Shot Learning répondent à une demande de direction : réaliser un état de l'art sur une technique de modélisation récente (moins de cinq ans) pour les données textuelles, afin d'évaluer si elle peut surpasser ou compléter les modèles classiques, notamment en termes de coût de calcul et de besoin en données. La veille s'est concentrée sur le Few-Shot Learning, une approche qui vise de hautes performances avec très peu de données annotées, un enjeu majeur pour réduire les coûts d'annotation. J'ai réalisé ce projet dans le cadre de ma formation de Data Scientist OpenClassrooms, en 2025. La mission initiale comprenait aussi un dashboard, qui a été intégré au projet de scoring de crédit pour former un projet MLOps complet ; ce dépôt se concentre donc sur la veille et le POC.

## Ce que j'ai fait (mon rôle personnel)

J'ai réalisé une veille technologique sur les méthodes récentes en NLP et sélectionné SetFit (Sentence Transformer Fine-tuning) pour sa promesse d'efficacité avec peu de données. J'ai établi une baseline performante en entraînant une régression logistique sur des embeddings all-MiniLM-L6-v2, avec 100 % des données d'entraînement (840 échantillons). J'ai mené un Proof of Concept en entraînant un modèle SetFit sur un sous-ensemble few-shot de seulement 112 échantillons, soit 16 par catégorie et 13 % des données. J'ai comparé les deux modèles sur le même jeu de test de 210 échantillons, avec le F1-Score pondéré. J'ai enfin rédigé une note méthodologique pour expliquer les concepts de SetFit (apprentissage contrastif et tête de classification) et présenter les conclusions.

## Technologies utilisées

J'ai utilisé Python, la librairie setfit, sentence-transformers, datasets de Hugging Face, Scikit-Learn (régression logistique et rapport de classification), Pandas, NumPy et Jupyter Notebook.

## Résultats

Le modèle SetFit atteint un F1-Score de 0,87, contre 0,93 pour la baseline en régression logistique. Autrement dit, SetFit atteint 93 % de la performance de la baseline en n'utilisant que 13 % des données d'entraînement (112 échantillons contre 840). Ce résultat valide son intérêt pour réduire les coûts d'annotation. Le code est disponible sur github.com/tmoahs/Veille-Technique-POC.

## Ce que j'en ai appris

Ce projet m'a fait pratiquer la veille technologique et scientifique : rechercher, analyser et synthétiser des articles de recherche en NLP et Few-Shot Learning. J'y ai conçu un Proof of Concept avec un protocole expérimental rigoureux pour comparer deux approches. J'ai approfondi mon usage de l'écosystème Hugging Face (sentence-transformers, datasets, setfit). J'ai aussi travaillé la communication technique, à travers la rédaction d'une note méthodologique destinée à vulgariser un concept complexe. Enfin, j'ai appris à évaluer un modèle non seulement sur sa performance brute, mais aussi sur son rapport performance / coût d'annotation.
