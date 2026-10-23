from datetime import timedelta
from datetime import datetime
from airflow.sdk import DAG
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.decorators import dag, task
from datetime import timedelta
from airflow.models.param import Param

default_args = {
    "retries": 2, # Nombre de relances en cas d'échec
    "retry_delay": timedelta(minutes=1), # Temps d'attente avant relance
    "execution_timeout": timedelta(minutes=15), # Coupe la tâche si elle bloque trop longtemps
}


@dag(
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    max_active_runs=1,
    params={"force_rebuild": Param(default=False, type="boolean")}
)
def ingestion_dag():
    @task
    def source_list():
        import os
        import hashlib
        from src.rag.config import KNOWLEDGE_DIR

        etat_fichiers = {}

        # On lit chaque fichier du dossier pour générer son empreinte unique
        if os.path.exists(KNOWLEDGE_DIR):
            for filename in os.listdir(KNOWLEDGE_DIR):
                filepath = os.path.join(KNOWLEDGE_DIR, filename)

                # On s'assure que c'est un fichier et non un sous-dossier
                if os.path.isfile(filepath):
                    with open(filepath, "rb") as f:
                        contenu = f.read()
                        etat_fichiers[filename] = hashlib.sha256(contenu).hexdigest()

        print(f"Nombre de fichiers analysés : {len(etat_fichiers)}")
        return etat_fichiers  # Ne retourne que des noms et des hashs légers !

    @task
    def tache_2(etat_actuel, **context):  # <-- Ajout de **context
        import psycopg
        from src.rag.config import DATABASE_URL

        force_rebuild = context["params"]["force_rebuild"]

        if force_rebuild:
            print("Mode RECONSTRUCTION COMPLÈTE activé !")
            return list(etat_actuel.keys())

        fichiers_a_traiter = []

        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                # 1. On s'assure que la table existe
                cur.execute("""
                            CREATE TABLE IF NOT EXISTS documents_state
                            (
                                filename     VARCHAR(255) PRIMARY KEY,
                                file_hash    VARCHAR(64) NOT NULL,
                                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            )
                            """)
                conn.commit()  # On valide la création

                # 2. On compare les hashs
                for nom_fichier, hash_actuel in etat_actuel.items():
                    cur.execute("SELECT file_hash FROM documents_state WHERE filename = %s", (nom_fichier,))
                    resultat = cur.fetchone()

                    if resultat is None:
                        fichiers_a_traiter.append(nom_fichier)
                    elif resultat[0] != hash_actuel:
                        fichiers_a_traiter.append(nom_fichier)

        print(f"Nombre de fichiers à traiter : {len(fichiers_a_traiter)}")
        return fichiers_a_traiter

    @task
    def chunking(fichiers_a_traiter):
        if not fichiers_a_traiter:
            print("Aucun fichier modifié, on passe.")
            return None

        import os
        import json
        from src.rag.config import KNOWLEDGE_DIR, CHUNK_SIZE
        from src.rag.loader import load_documents
        from src.rag.chunker import chunk_all_documents

        # Charge tous les documents et filtre ceux qui doivent être traités
        tous_les_docs = load_documents(KNOWLEDGE_DIR)
        docs_a_traiter = [d for d in tous_les_docs if d["source"] in fichiers_a_traiter]

        print(f"Découpage de {len(docs_a_traiter)} fichiers...")
        chunks = chunk_all_documents(docs_a_traiter, max_chunk_size=CHUNK_SIZE)

        # Sauvegarde sur le volume partagé
        os.makedirs("/opt/airflow/staging", exist_ok=True)
        chemin_staging = "/opt/airflow/staging/chunks_temp.json"

        with open(chemin_staging, "w", encoding="utf-8") as f:
            json.dump(chunks, f)

        return chemin_staging

    @task
    def embeddings(chemin_chunks):
        if not chemin_chunks:
            return None

        import json
        from src.rag.embeddings import embed_documents

        with open(chemin_chunks, "r", encoding="utf-8") as f:
            chunks = json.load(f)

        print(f"Vectorisation de {len(chunks)} chunks...")
        textes = [c["text"] for c in chunks]
        vecteurs = embed_documents(textes)

        chemin_embeds = "/opt/airflow/staging/embeddings_temp.json"
        with open(chemin_embeds, "w", encoding="utf-8") as f:
            json.dump(vecteurs, f)

        return chemin_embeds

    @task
    def ajout_chroma(chemin_chunks, chemin_embeddings):
        if not chemin_chunks or not chemin_embeddings:
            return "Rien à insérer"

        import json
        from src.rag.vectorstore import get_collection, upsert_chunks

        with open(chemin_chunks, "r", encoding="utf-8") as f:
            chunks = json.load(f)
        with open(chemin_embeddings, "r", encoding="utf-8") as f:
            vecteurs = json.load(f)

        print(f"Upsert de {len(chunks)} éléments dans ChromaDB...")
        collection = get_collection()
        upsert_chunks(collection, chunks, vecteurs)

        return "Upsert terminé"

    @task
    def obsolete(etat_actuel):
        import psycopg
        from src.rag.config import DATABASE_URL
        from src.rag.vectorstore import get_collection

        fichiers_supprimes = []

        # 1. On cherche les fichiers qui sont dans la base mais plus sur le disque
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                # On s'assure que la table existe (au cas où cette tâche tourne très tôt)
                cur.execute(
                    "CREATE TABLE IF NOT EXISTS documents_state (filename VARCHAR(255) PRIMARY KEY, file_hash VARCHAR(64) NOT NULL, last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")

                cur.execute("SELECT filename FROM documents_state")
                lignes = cur.fetchall()
                for ligne in lignes:
                    nom_fichier = ligne[0]
                    if nom_fichier not in etat_actuel:
                        fichiers_supprimes.append(nom_fichier)

        # 2. Si on a trouvé des fichiers supprimés, on nettoie Chroma et Postgres
        if fichiers_supprimes:
            print(f"Nettoyage de {len(fichiers_supprimes)} fichiers obsolètes : {fichiers_supprimes}")
            collection = get_collection()

            with psycopg.connect(DATABASE_URL) as conn:
                with conn.cursor() as cur:
                    for nom_fichier in fichiers_supprimes:
                        # Suppression dans ChromaDB (via la métadonnée 'source')
                        collection.delete(where={"source": nom_fichier})
                        # Suppression dans Postgres
                        cur.execute("DELETE FROM documents_state WHERE filename = %s", (nom_fichier,))
                conn.commit()
        else:
            print("Aucun fichier obsolète à nettoyer.")

        return fichiers_supprimes

    @task
    def verif(statut_ajout, statut_obsolete):
        from src.rag.vectorstore import get_collection

        collection = get_collection()
        # count() renvoie le nombre total de chunks actuellement stockés
        total_chunks = collection.count()

        print(f"--- Bilan ChromaDB ---")
        print(f"La collection contient actuellement {total_chunks} chunks vectorisés prêts pour le RAG.")

        if total_chunks == 0:
            print("Attention : La collection est vide !")

        return total_chunks

    @task
    def save(statut_verif, etat_actuel):
        import psycopg
        from src.rag.config import DATABASE_URL

        if not etat_actuel:
            return "Aucun état à sauvegarder."

        print("Mise à jour des empreintes dans la base de données...")

        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                for nom_fichier, hash_fichier in etat_actuel.items():
                    # L'instruction UPSERT de Postgres : on insère, ou on met à jour si ça existe déjà
                    cur.execute("""
                                INSERT INTO documents_state (filename, file_hash, last_updated)
                                VALUES (%s, %s, CURRENT_TIMESTAMP)
                                ON CONFLICT (filename)
                                    DO UPDATE SET file_hash    = EXCLUDED.file_hash,
                                                  last_updated = CURRENT_TIMESTAMP
                                """, (nom_fichier, hash_fichier))
            conn.commit()

        return "Synchronisation terminée avec succès."

    # ENCHAÎNEMENT DE TES TÂCHES (Le Pipeline)

    etat = source_list()
    a_traiter = tache_2(etat)

    fichier_chunks = chunking(a_traiter)
    fichier_embeds = embeddings(fichier_chunks)
    statut_ajout = ajout_chroma(fichier_chunks, fichier_embeds)

    statut_obsolete = obsolete(etat)

    # On attend la fin des ajouts et suppressions pour compter
    statut_verif = verif(statut_ajout, statut_obsolete)

    # On sauvegarde l'état à la toute fin
    save(statut_verif, etat)

ingestion_dag()