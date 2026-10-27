"""Génère des secrets d'exploitation pour la production.

Aucun secret n'est écrit sur le disque : le script affiche un bloc à coller
dans `.env.prod` (créé sur le serveur, jamais commité).

    python scripts/gen_secrets.py
"""

import base64
import secrets
import string


def strong_password(length: int = 32) -> str:
    alphabet = string.ascii_letters + string.digits + "-_"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def fernet_key() -> str:
    """Clé Fernet attendue par Airflow (32 octets encodés en base64 url-safe)."""
    return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode("ascii")


def main() -> None:
    print("# --- Secrets générés le", flush=True)
    print("#     Colle ce bloc dans .env.prod puis : chmod 600 .env.prod")
    print("#     Conserve une copie dans ton gestionnaire de mots de passe.\n")
    print(f"POSTGRES_PASSWORD={strong_password(40)}")
    print(f"_AIRFLOW_WWW_USER_PASSWORD={strong_password(32)}")
    print(f"FERNET_KEY={fernet_key()}")
    print(f"AIRFLOW__API_AUTH__JWT_SECRET={strong_password(48)}")


if __name__ == "__main__":
    main()
