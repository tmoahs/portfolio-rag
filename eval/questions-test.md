# Questions-test pour le chatbot

Ce fichier propose, pour chaque fichier produit, 5 questions qu'un recruteur pourrait poser, la réponse attendue et le fichier source. Il sert à tester le chatbot RAG.

---

## parcours.md

**Q1. Quelles sont les expériences professionnelles de Thomas Patout ?**
R : Il a été traducteur freelance sur Upwork de 2020 à novembre 2025, a effectué un service civique au CHRU Hôpitaux de Tours (Hôpital Trousseau) d'octobre 2023 à mai 2024, et est Data Scientist freelance sur Upwork depuis novembre 2025. Source : parcours.md.

**Q2. Quelle est son expérience de traducteur ?**
R : Traducteur freelance sur Upwork de 2020 à novembre 2025, traduction anglais vers français d'articles scientifiques, d'interviews et de cours, note 5/5 et plus de 20 000 € de missions livrées. Source : parcours.md.

**Q3. A-t-il réalisé des missions en tant que Data Scientist freelance ?**
R : Non, il est inscrit comme Data Scientist freelance sur Upwork depuis novembre 2025 mais n'a pas encore réalisé de mission. Source : parcours.md.

**Q4. En quoi a consisté son service civique ?**
R : Au CHRU Hôpitaux de Tours, Hôpital Trousseau, d'octobre 2023 à mai 2024, il accueillait et orientait les usagers, en gérant le stress et en priorisant les demandes. Source : parcours.md.

**Q5. Quelle est sa nationalité et est-il mobile ?**
R : Il est de nationalité française et se déclare mobile. Source : parcours.md (et recherche-emploi.md).

---

## formation.md

**Q1. Quelle formation a suivie Thomas Patout en data science ?**
R : La formation de Data Scientist d'OpenClassrooms, de 2024 à 2025, sanctionnée par le titre RNCP Niveau 7 (Bac+5), avec 9 projets de bout en bout. Source : formation.md.

**Q2. Quel diplôme a-t-il avant la data science ?**
R : Un cursus de licence de psychologie à l'Université de Tours (2019–2022, dont une année d'échange en 2021–2022 à l'Université du Québec à Trois-Rivières) et un master de psychologie du travail à l'Université de Tours (2022–2023, interrompu pour se réorienter). Source : formation.md.

**Q3. Quel est son niveau d'anglais ?**
R : Niveau C1, avec un score de 985/990 au TOEIC. Source : formation.md.

**Q4. Combien de projets compte sa formation ?**
R : 9 projets de formation. Le projet Events Curator est un projet personnel réalisé en dehors de la formation. Source : formation.md.

**Q5. Pourquoi s'est-il réorienté vers la data science ?**
R : Son master de psychologie du travail (2022–2023) a été interrompu suite à des problèmes administratifs, et il s'est alors réorienté vers la data science. Source : formation.md.

---

## competences.md

**Q1. Quelles compétences utilise-t-il en production ?**
R : Python, LightGBM, Docker, FastAPI, CI/CD, MLflow, Streamlit, SHAP et Evidently AI, utilisés sur le projet de scoring de crédit. Source : competences.md.

**Q2. Où a-t-il utilisé SQL ?**
R : SQL a été utilisé pour l'analyse exploratoire dans le projet de segmentation de clients e-commerce. Source : competences.md.

**Q3. Où a-t-il utilisé XGBoost ?**
R : Dans les notebooks des projets Prédiction de la consommation énergétique de bâtiments et Scoring de crédit. Source : competences.md.

**Q4. Quelles compétences relèvent de l'automatisation IA ?**
R : n8n, les LLM APIs et Google Gemini API, utilisés sur le projet personnel AI Cultural Events Curator. Source : competences.md.

**Q5. Dans quel projet a-t-il utilisé PySpark ?**
R : Dans le projet Pipeline Big Data AgriTech, avec AWS EMR et S3. Source : competences.md.

---

## recherche-emploi.md

**Q1. Quel poste et quel contrat recherche-t-il ?**
R : Un CDI dans la data, en priorité comme Data Scientist, et il est aussi en recherche sur les métiers de Data Engineer et d'AI Engineer. Il reste ouvert aux intitulés proches (Data Analyst, ML Engineer / MLOps junior, AI / LLM Automation Engineer, Analytics Engineer, Data Product Manager / PO IA junior). Source : recherche-emploi.md.

**Q2. Cible-t-il une ville en particulier ?**
R : Non, il ne cible aucune ville en particulier et cherche partout, avec des versions de CV pour la France, la Suisse romande et le Québec. Source : recherche-emploi.md.

**Q3. Quand est-il disponible ?**
R : Il est disponible immédiatement, mobile et titulaire du permis B. Source : recherche-emploi.md.

**Q4. Quelle est sa position sur le télétravail ?**
R : Le télétravail lui est indifférent : présentiel, hybride ou full remote. Source : recherche-emploi.md.

**Q5. Quelle est sa rémunération cible ?**
R : Il ne communique pas de fourchette fixe, car les écarts de salaire varient fortement selon les régions ; il aborde la rémunération au cas par cas selon les offres. Source : recherche-emploi.md.

---

## centres-interet.md

**Q1. Quels sont les centres d'intérêt de Thomas Patout ?**
R : Le cinéma, la composition MAO et les échecs. Source : centres-interet.md.

**Q2. Fait-il de la musique ?**
R : Oui, la composition MAO (musique assistée par ordinateur) est l'un de ses centres d'intérêt. Source : centres-interet.md.

**Q3. Joue-t-il aux échecs ?**
R : Oui, les échecs sont l'un de ses centres d'intérêt. Source : centres-interet.md.

**Q4. Quels films apprécie-t-il ?**
R : Il cite Barry Lyndon, Once Upon A Time In Hollywood, Fallen Angels, Blade Runner, Heat, Ran et Entre le ciel et l'enfer. Source : centres-interet.md.

**Q5. Quels outils de MAO utilise-t-il et dans quel style ?**
R : Il compose sur Ableton Live, dans un registre de musique électronique ; ses projets musicaux sont privés. Source : centres-interet.md.

---

## projet-scoring-credit.md

**Q1. Quel est le résultat principal du projet de scoring de crédit ?**
R : Un modèle LGBM avec un AUC de 0,79, déployé via une API FastAPI et un dashboard Streamlit. Source : projet-scoring-credit.md.

**Q2. Pourquoi avoir utilisé un score métier plutôt que l'accuracy ?**
R : Parce que les deux erreurs possibles n'ont pas le même coût : refuser un bon client fait perdre une marge, accepter un mauvais payeur fait perdre le capital. Le seuil de décision est optimisé sur cette fonction de coût au lieu de 0,5. Source : projet-scoring-credit.md.

**Q3. Quelles technologies a-t-il utilisées sur ce projet ?**
R : Python, LightGBM, FastAPI, Docker, CI/CD, MLflow, Streamlit, SHAP, Evidently AI, SQLite et Pandas. Source : projet-scoring-credit.md.

**Q4. Comment le modèle est-il déployé ?**
R : Via une API FastAPI conteneurisée avec Docker, avec des tests automatisés et un pipeline CI/CD (workflow GitHub Actions), et un dashboard Streamlit qui consomme l'API. Les deux sont en ligne. Source : projet-scoring-credit.md.

**Q5. À quoi sert Evidently AI dans ce projet ?**
R : À générer un rapport de monitoring de dérive des données en production. Source : projet-scoring-credit.md.

---

## projet-events-curator.md

**Q1. Que fait l'AI Cultural Events Curator ?**
R : Un workflow automatisé où un utilisateur remplit un formulaire (ville, catégorie, style) et reçoit un email HTML avec 5 événements culturels réels, chacun accompagné d'une description personnalisée générée par IA. Source : projet-events-curator.md.

**Q2. Comment le coût est-il maintenu à zéro ?**
R : Le workflow tourne sur des paliers gratuits (n8n local, Ticketmaster, Gemini) et regroupe les 5 événements en un seul appel à Google Gemini pour générer les 5 descriptions. Source : projet-events-curator.md.

**Q3. Quelles API utilise ce projet ?**
R : L'API Ticketmaster (données d'événements), l'API Google Gemini (descriptions) et l'API Gmail (envoi). Source : projet-events-curator.md.

**Q4. Est-ce un projet de formation ou un projet personnel ?**
R : Un projet personnel, réalisé en 2026. Source : projet-events-curator.md.

**Q5. Pourquoi une étape de déduplication ?**
R : Sur 20 événements récupérés, beaucoup se répètent ; la déduplication ramène l'ensemble à 5 événements réellement distincts, sans quoi l'email perd tout intérêt. Source : projet-events-curator.md.

---

## projet-prediction-consommation-batiments.md

**Q1. Quel est le résultat du projet de prédiction de consommation de bâtiments ?**
R : Une régression LightGBM atteignant un R² de 0,85 après un important feature engineering. Source : projet-prediction-consommation-batiments.md.

**Q2. Quel objectif métier ce projet sert-il ?**
R : Anticiper la consommation et les émissions de CO2 des bâtiments pour cibler les rénovations les plus rentables. Source : projet-prediction-consommation-batiments.md.

**Q3. Comment l'explicabilité est-elle traitée ?**
R : Par une analyse SHAP, qui identifie les principaux leviers d'optimisation énergétique et explique les prédictions du modèle. Source : projet-prediction-consommation-batiments.md.

**Q4. Quelles technologies sont utilisées ?**
R : Python, Scikit-Learn, LightGBM, SHAP, Pandas, NumPy, Matplotlib, Seaborn et Jupyter Notebook. Source : projet-prediction-consommation-batiments.md.

**Q5. S'agit-il d'un projet de formation ?**
R : Oui, réalisé dans le cadre de la formation de Data Scientist OpenClassrooms en 2025. Source : projet-prediction-consommation-batiments.md.

---

## projet-classification-multimodale-produits.md

**Q1. Quel est le résultat du projet de classification multimodale ?**
R : Un classifieur qui atteint une accuracy de 81,3 % en exploitant le texte (BERT) et les images (CNN) des produits. Source : projet-classification-multimodale-produits.md.

**Q2. Qu'est-ce qui rend ce projet « multimodal » ?**
R : Il exploite deux types de données non structurées : les descriptions textuelles des produits (NLP) et leurs visuels (vision par ordinateur). Source : projet-classification-multimodale-produits.md.

**Q3. Quelles techniques de feature engineering a-t-il utilisées ?**
R : TF-IDF pour le texte et SIFT pour les images. Source : projet-classification-multimodale-produits.md.

**Q4. Quelles technologies sont utilisées ?**
R : Python, Scikit-Learn, Pandas, NLTK, Pillow, OpenCV, TensorFlow/Keras, BERT, TF-IDF, SIFT et Jupyter Notebook. Source : projet-classification-multimodale-produits.md.

**Q5. Le projet combine-t-il le texte et les images dans un seul modèle ?**
R : Non, le modèle final est un CNN entraîné sur les images (accuracy d'environ 80 %, soit 81,3 %). L'approche texte a été validée séparément avec BERT, et combiner le texte et l'image a été identifié comme une amélioration possible. Source : projet-classification-multimodale-produits.md.

---

## projet-segmentation-clients-ecommerce.md

**Q1. Quel est l'objectif du projet de segmentation de clients e-commerce ?**
R : Regrouper les clients d'un site marchand en profils distincts pour définir des actions marketing ciblées. Source : projet-segmentation-clients-ecommerce.md.

**Q2. Quelles méthodes de segmentation a-t-il utilisées ?**
R : Une analyse RFM, une ACP et un clustering K-Means complété par DBSCAN. Source : projet-segmentation-clients-ecommerce.md.

**Q3. Comment a-t-il validé les segments ?**
R : Par une analyse de stabilité (score ARI) sur 6 mois, qui a validé la pertinence des segments et guidé la fréquence de réentraînement. Source : projet-segmentation-clients-ecommerce.md.

**Q4. Quel rôle a joué SQL dans ce projet ?**
R : SQL a servi à l'analyse exploratoire, pour interroger directement la base de données clients. Source : projet-segmentation-clients-ecommerce.md.

**Q5. Quels segments a-t-il identifiés ?**
R : Par exemple 3 segments pour les nouveaux clients et 5 segments pour les clients fidèles. Source : projet-segmentation-clients-ecommerce.md.

---

## projet-pipeline-big-data-agritech.md

**Q1. Quel était l'enjeu du projet Pipeline Big Data AgriTech ?**
R : Bâtir une chaîne de traitement capable de passer de quelques milliers à plusieurs millions d'images sans être refaite de zéro, dans un scénario de start-up AgriTech. Source : projet-pipeline-big-data-agritech.md.

**Q2. Quelle architecture a-t-il mise en place ?**
R : Une architecture cloud-native S3 → EMR → S3, sans stockage intermédiaire local. Source : projet-pipeline-big-data-agritech.md.

**Q3. Comment a-t-il optimisé l'usage du modèle sur le cluster ?**
R : En diffusant les poids de MobileNetV2 via le broadcast (une seule diffusion vers tous les nœuds) et en parallélisant l'inférence image avec des Pandas UDF. Source : projet-pipeline-big-data-agritech.md.

**Q4. Quel est le résultat de la réduction de dimension ?**
R : Une PCA sous PySpark ML ramène les features de 1280 à 100 composantes, ce qui réduit fortement le volume stocké et lu. Source : projet-pipeline-big-data-agritech.md.

**Q5. Comment la conformité RGPD a-t-elle été assurée ?**
R : Les serveurs S3 et EMR sont configurés en Europe. Source : projet-pipeline-big-data-agritech.md.

---

## projet-veille-few-shot-setfit.md

**Q1. Quel est le résultat de la veille et du POC Few-Shot Learning ?**
R : SetFit atteint un F1-Score de 0,87 contre 0,93 pour la baseline, soit 93 % de la performance de la baseline avec seulement 13 % des données (112 échantillons contre 840). Source : projet-veille-few-shot-setfit.md.

**Q2. Quelle technique a-t-il sélectionnée et pourquoi ?**
R : SetFit (Sentence Transformer Fine-tuning), pour sa promesse d'efficacité avec peu de données annotées. Source : projet-veille-few-shot-setfit.md.

**Q3. Comment la baseline a-t-elle été construite ?**
R : Une régression logistique entraînée sur des embeddings all-MiniLM-L6-v2, avec 100 % des données d'entraînement (840 échantillons). Source : projet-veille-few-shot-setfit.md.

**Q4. Sur quel jeu de test les modèles ont-ils été comparés ?**
R : Sur le même jeu de test de 210 échantillons, avec le F1-Score pondéré. Source : projet-veille-few-shot-setfit.md.

**Q5. Pourquoi ce dépôt ne contient-il pas de dashboard ?**
R : Le dashboard prévu dans la mission initiale a été intégré au projet de scoring de crédit ; ce dépôt se concentre sur la veille et le POC. Source : projet-veille-few-shot-setfit.md.

---

## projet-cadrage-pilotage-ia.md

**Q1. Quel rôle Thomas Patout a-t-il tenu dans ce projet ?**
R : Un rôle d'AI Product Manager et de Scrum Master, chargé de structurer le projet de A à Z pour le présenter au COMEX. Source : projet-cadrage-pilotage-ia.md.

**Q2. Quel est le résultat financier du projet ?**
R : Un investissement total de 22 550 €, un gain annuel projeté de 30 000 € et un ROI positif dès la première année (+3 480 €). Ces montants proviennent d'un scénario fictif de cadrage : il ne s'agit pas d'argent réel. Source : projet-cadrage-pilotage-ia.md.

**Q3. Comment a-t-il priorisé le backlog ?**
R : Avec la méthode MoSCoW (Must, Should, Could, Won't). Source : projet-cadrage-pilotage-ia.md.

**Q4. Comment les photos des utilisateurs sont-elles traitées au regard du RGPD ?**
R : Elles sont classées comme données sensibles nécessitant un consentement explicite, avec des mesures de sécurité, des destinataires définis et une durée de conservation de 3 ans après inactivité. Source : projet-cadrage-pilotage-ia.md.

**Q5. Quels risques a-t-il identifiés ?**
R : Des risques techniques (modèle « boîte noire »), humains (disponibilité des développeurs), concurrentiels (lancement d'un concurrent) et légaux (RGPD). Source : projet-cadrage-pilotage-ia.md.

---

## projet-preparation-donnees-sante-publique.md

**Q1. Quel était l'objectif du projet de préparation de données de santé publique ?**
R : Nettoyer et préparer les données Open Food Facts pour évaluer la faisabilité d'un système d'auto-complétion des informations nutritionnelles. Source : projet-preparation-donnees-sante-publique.md.

**Q2. Comment a-t-il traité les valeurs manquantes ?**
R : Par une imputation KNN (KNN Imputer). Source : projet-preparation-donnees-sante-publique.md.

**Q3. Quel est le résultat principal ?**
R : L'ANOVA a validé que des catégories clés comme le Nutri-Score expliquent significativement la composition des produits, ce qui confirme la viabilité du système. Source : projet-preparation-donnees-sante-publique.md.

**Q4. Quelles analyses statistiques a-t-il menées ?**
R : Une ACP et une ANOVA, dans le cadre d'analyses univariées et multivariées. Source : projet-preparation-donnees-sante-publique.md.

**Q5. Quelles technologies sont utilisées ?**
R : Python, Pandas, NumPy, Matplotlib, Seaborn, l'imputation KNN, l'ACP, l'ANOVA et Jupyter Notebook. Source : projet-preparation-donnees-sante-publique.md.

---

## projet-analyse-systemes-educatifs.md

**Q1. Quel est l'objectif du projet d'analyse de systèmes éducatifs ?**
R : Réaliser une analyse exploratoire (EDA) complète de données de systèmes éducatifs mondiaux, avec un nettoyage et une manipulation des données. Source : projet-analyse-systemes-educatifs.md.

**Q2. Quel est le résultat principal ?**
R : La construction d'un score composite pour évaluer et classer les pays selon leurs performances éducatives. Source : projet-analyse-systemes-educatifs.md.

**Q3. Quel type d'analyse a-t-il menée ?**
R : Une analyse exploratoire univariée, pour comprendre la distribution et les caractéristiques de chaque variable. Source : projet-analyse-systemes-educatifs.md.

**Q4. Quelles technologies sont utilisées ?**
R : Python, Pandas, Matplotlib, Seaborn et Jupyter Notebook. Source : projet-analyse-systemes-educatifs.md.

**Q5. Est-ce un projet avancé ou un projet de fondation ?**
R : Un projet de fondation, destiné à maîtriser les premières étapes d'une analyse : manipulation des données et exploration univariée. Source : projet-analyse-systemes-educatifs.md.
