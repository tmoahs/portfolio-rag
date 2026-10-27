"""Crée `.env.prod` à partir de `.env.prod.example`, avec des secrets générés.

    python3 scripts/init_prod_env.py --domain tpatout.fr --email t.patout@proton.me

La clé Gemini est demandée en saisie masquée (elle n'apparaît ni à l'écran ni
dans l'historique du shell). Le fichier est écrit avec les droits 600.

    --force   écrase un .env.prod existant (fait une sauvegarde .bak)
"""

import argparse
import base64
import getpass
import os
import re
import secrets
import string
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXAMPLE = ROOT / ".env.prod.example"
TARGET = ROOT / ".env.prod"

KEY_RE = re.compile(r"^([A-Z_][A-Z0-9_]*)=")


def strong_password(length: int = 40) -> str:
    alphabet = string.ascii_letters + string.digits + "-_"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def fernet_key() -> str:
    return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode("ascii")


def ask(prompt: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{prompt}{suffix} : ").strip()
    return value or (default or "")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--domain", help="ex. tpatout.fr")
    parser.add_argument("--email", help="email ACME (Let's Encrypt)")
    parser.add_argument("--gemini-key", help="clé Gemini (sinon saisie masquée)")
    parser.add_argument("--force", action="store_true", help="écrase .env.prod")
    args = parser.parse_args()

    if not EXAMPLE.exists():
        print(f"{EXAMPLE.name} introuvable : lance ce script depuis le dépôt.", file=sys.stderr)
        return 1

    if TARGET.exists() and not args.force:
        print(".env.prod existe déjà. Utilise --force pour le remplacer.", file=sys.stderr)
        return 1

    domain = (args.domain or ask("Domaine (sans https://)")).strip().lower().rstrip("/")
    if not domain or " " in domain or "/" in domain:
        print("Domaine invalide.", file=sys.stderr)
        return 1

    email = (args.email or ask("Email ACME")).strip()
    if "@" not in email:
        print("Email invalide.", file=sys.stderr)
        return 1

    gemini = (args.gemini_key or getpass.getpass("Clé Gemini (saisie masquée) : ")).strip()
    if not gemini:
        print("Clé Gemini manquante.", file=sys.stderr)
        return 1

    overrides = {
        "DOMAIN": domain,
        "ACME_EMAIL": email,
        "GEMINI_API_KEY": gemini,
        "POSTGRES_PASSWORD": strong_password(40),
        "FERNET_KEY": fernet_key(),
        "AIRFLOW__API_AUTH__JWT_SECRET": strong_password(48),
        "_AIRFLOW_WWW_USER_PASSWORD": strong_password(32),
        "_AIRFLOW_WWW_USER_EMAIL": email,
        "ALLOWED_ORIGINS": f"https://{domain}",
    }

    lines = EXAMPLE.read_text(encoding="utf-8").splitlines()
    written = set()
    output = []

    for line in lines:
        match = KEY_RE.match(line)
        if match and match.group(1) in overrides:
            key = match.group(1)
            output.append(f"{key}={overrides[key]}")
            written.add(key)
        else:
            output.append(line)

    missing = [key for key in overrides if key not in written]
    if missing:
        output.append("")
        output.append("# --- Complété par init_prod_env.py ---")
        output.extend(f"{key}={overrides[key]}" for key in missing)

    if TARGET.exists():
        TARGET.replace(TARGET.with_suffix(".bak"))

    TARGET.write_text("\n".join(output) + "\n", encoding="utf-8")
    os.chmod(TARGET, 0o600)

    print(f"\n{TARGET.name} créé (droits 600).")
    print(f"DOMAIN={domain}")
    print(f"ALLOWED_ORIGINS=https://{domain}")
    print("Secrets générés : POSTGRES_PASSWORD, FERNET_KEY, JWT Airflow, admin Airflow.")
    print("Sauvegarde ce fichier dans ton gestionnaire de mots de passe.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
