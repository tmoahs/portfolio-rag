"""Supprime les échanges plus anciens que la durée de conservation.

À lancer par cron (ou depuis le DAG `maintenance_dag`) une fois par jour :

    python scripts/purge_old_data.py            # utilise RETENTION_DAYS (.env)
    python scripts/purge_old_data.py --days 180

Les retours (feedbacks) et les chunks associés sont supprimés en cascade.
"""

import argparse
import os
import sys

from dotenv import load_dotenv

load_dotenv()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--days",
        type=int,
        default=int(os.getenv("RETENTION_DAYS", "365")),
        help="Durée de conservation en jours (défaut : RETENTION_DAYS)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Compte les lignes concernées sans rien supprimer",
    )
    parser.add_argument(
        "--cache-days",
        type=int,
        default=int(os.getenv("CACHE_TTL_DAYS", "7")),
        help="Durée de vie des réponses en cache (défaut : CACHE_TTL_DAYS)",
    )
    args = parser.parse_args()

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL manquant.", file=sys.stderr)
        return 1

    if args.days <= 0:
        print("Durée invalide : elle doit être strictement positive.", file=sys.stderr)
        return 1

    import psycopg

    with psycopg.connect(database_url, connect_timeout=10) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT to_regclass('public.answer_cache');")
            has_cache = cur.fetchone()[0] is not None

            if args.dry_run:
                cur.execute(
                    "SELECT count(*) FROM exchanges "
                    "WHERE created_at < NOW() - make_interval(days => %s);",
                    (args.days,),
                )
                print(f"{cur.fetchone()[0]} échange(s) seraient supprimés.")

                if has_cache:
                    cur.execute(
                        "SELECT count(*) FROM answer_cache "
                        "WHERE created_at < NOW() - make_interval(days => %s);",
                        (args.cache_days,),
                    )
                    print(f"{cur.fetchone()[0]} réponse(s) en cache seraient supprimées.")
                return 0

            cur.execute(
                "DELETE FROM exchanges "
                "WHERE created_at < NOW() - make_interval(days => %s);",
                (args.days,),
            )
            deleted = cur.rowcount

            cache_deleted = 0
            if has_cache:
                cur.execute(
                    "DELETE FROM answer_cache "
                    "WHERE created_at < NOW() - make_interval(days => %s);",
                    (args.cache_days,),
                )
                cache_deleted = cur.rowcount
        conn.commit()

    print(f"{deleted} échange(s) supprimé(s) (conservation : {args.days} jours).")
    if cache_deleted:
        print(f"{cache_deleted} réponse(s) retirée(s) du cache (TTL : {args.cache_days} jours).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
