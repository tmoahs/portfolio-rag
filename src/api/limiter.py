import os

from slowapi import Limiter
from slowapi.util import get_remote_address

# Derrière le reverse proxy, request.client.host vaut l'IP du proxy : il faut
# alors lire X-Forwarded-For (posé par Caddy). Ne jamais activer TRUST_PROXY
# si l'API est joignable directement, sinon l'en-tête est falsifiable.
TRUST_PROXY = os.getenv("TRUST_PROXY", "0") == "1"


def client_key(request) -> str:
    """Clé de limitation : IP réelle du client, jamais celle du proxy."""
    if TRUST_PROXY:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip.strip()

    return get_remote_address(request)


limiter = Limiter(key_func=client_key)
