# AI Cultural Events Curator

## Contexte

L'AI Cultural Events Curator est un projet personnel que j'ai réalisé en 2026. Il part d'un problème du quotidien : trouver une sortie culturelle qui corresponde vraiment à ses goûts demande du temps, car il faut ouvrir plusieurs sites et recouper les annonces pour finalement retomber sur les mêmes événements. Les recommandations proposées sont soit génériques, soit noyées dans du bruit. L'objectif du projet était double : proposer une recommandation réellement personnalisée, et le faire avec un coût d'exploitation nul. Cette contrainte de coût n'était pas un détail, c'est elle qui a structuré toutes les décisions techniques.

## Ce que j'ai fait (mon rôle personnel)

J'ai conçu et construit un workflow d'automatisation complet. Un utilisateur remplit un formulaire n8n minimal (ville, catégorie, style artistique), sans compte à créer ni application à installer. Le workflow interroge ensuite l'API Ticketmaster pour récupérer 20 événements réels, puis filtre les doublons pour n'en garder que 5 réellement distincts. J'ai agrégé les données de ces 5 événements et les ai envoyées en un seul appel à Google Gemini, qui génère les 5 descriptions personnalisées. J'ai enfin construit un email HTML lisible partout, avec du CSS en ligne imposé par Gmail, et je l'envoie via l'API Gmail. L'ensemble du workflow est porté par n8n, donc sans front-end à maintenir.

## Technologies utilisées

J'ai utilisé n8n pour l'orchestration, l'API Ticketmaster pour les données d'événements, l'API Google Gemini pour la génération de texte, l'API Gmail pour l'envoi et des API REST de manière générale.

## Résultats

Le workflow fonctionne de bout en bout et enchaîne 6 étapes automatisées. Son coût de fonctionnement mensuel est de 0 €, car il tourne entièrement sur des paliers gratuits (n8n local, Ticketmaster, Gemini). Une seule requête IA suffit pour générer les 5 descriptions, ce qui permet de rester dans le palier gratuit tout en préservant la personnalisation selon le style demandé par l'utilisateur. Le code est disponible sur github.com/tmoahs/Events-Curator.

## Difficultés rencontrées et solutions

Sur l'AI Cultural Events Curator, une première difficulté venait de la redondance : sur les 20 événements récupérés, beaucoup se répètent ou se ressemblent, ce qui privait l'email de tout intérêt ; j'ai ajouté une étape de filtrage qui ramène l'ensemble à 5 événements réellement distincts. La contrainte de coût était un deuxième obstacle : faire 5 appels séparés à Google Gemini aurait fait sortir du palier gratuit ; j'ai donc agrégé les données pour tout envoyer en un seul appel qui génère les 5 descriptions. Le format d'email a aussi imposé une contrainte technique, puisque Gmail exige du CSS en ligne, ce que j'ai respecté pour construire un email HTML lisible partout. Certaines limites subsistent : Ticketmaster est orienté concerts et sous-représente les expositions (piste : ajouter Eventbrite), la déduplication se base sur le titre, donc un spectacle à l'affiche plusieurs jours peut encore apparaître deux fois, et Gemini produit parfois une description générique sur un événement peu documenté (piste : scinder le workflow en deux appels).

## Ce que j'en ai appris

J'ai retenu que le coût se décide dès la conception : concevoir le prompt en fonction du palier gratuit a influencé l'architecture de tout le workflow. J'ai aussi appris que la qualité des données d'entrée fait la qualité de la sortie, puisque sans l'étape de déduplication l'IA aurait produit cinq descriptions du même concert. Enfin, j'ai compris qu'un bon projet documente aussi ses limites, car savoir dire ce qui ne fonctionne pas encore rend le reste plus crédible.
