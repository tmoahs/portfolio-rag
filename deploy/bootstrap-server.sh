#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Durcissement d'un VPS Debian/Ubuntu neuf, AVANT tout déploiement.
#
#   scp deploy/bootstrap-server.sh root@SERVEUR:/root/
#   ssh root@SERVEUR 'bash /root/bootstrap-server.sh "ssh-ed25519 AAAA... contact@laptop"'
#
# Le second argument est la clé publique SSH autorisée pour l'utilisateur de
# déploiement. Sans elle, aucun accès par clé ne sera possible : ne coupe pas
# ta session root avant d'avoir testé la connexion `ssh deploy@SERVEUR`.
# ---------------------------------------------------------------------------
set -euo pipefail

DEPLOY_USER="${DEPLOY_USER:-deploy}"
SSH_PORT="${SSH_PORT:-22}"
PUBLIC_KEY="${1:-}"

if [[ $EUID -ne 0 ]]; then
  echo "Ce script doit être lancé en root." >&2
  exit 1
fi

if [[ -z "$PUBLIC_KEY" ]]; then
  echo "Usage : $0 \"ssh-ed25519 AAAA... commentaire\"" >&2
  exit 1
fi

echo "==> 1/6 Utilisateur non privilégié : $DEPLOY_USER"
if ! id -u "$DEPLOY_USER" >/dev/null 2>&1; then
  adduser --disabled-password --gecos "" "$DEPLOY_USER"
fi
usermod -aG sudo "$DEPLOY_USER"

# Mot de passe désactivé + connexion par clé : sudo sans mot de passe pour ce compte.
echo "$DEPLOY_USER ALL=(ALL) NOPASSWD:ALL" > "/etc/sudoers.d/90-$DEPLOY_USER"
chmod 440 "/etc/sudoers.d/90-$DEPLOY_USER"
visudo -cf "/etc/sudoers.d/90-$DEPLOY_USER" >/dev/null

install -d -m 700 -o "$DEPLOY_USER" -g "$DEPLOY_USER" "/home/$DEPLOY_USER/.ssh"
printf '%s\n' "$PUBLIC_KEY" > "/home/$DEPLOY_USER/.ssh/authorized_keys"
chown "$DEPLOY_USER:$DEPLOY_USER" "/home/$DEPLOY_USER/.ssh/authorized_keys"
chmod 600 "/home/$DEPLOY_USER/.ssh/authorized_keys"

echo "==> 2/6 Durcissement SSH (clé uniquement, root interdit)"
install -d -m 755 /etc/ssh/sshd_config.d
cat > /etc/ssh/sshd_config.d/99-portfolio.conf <<EOF
PermitRootLogin no
PasswordAuthentication no
KbdInteractiveAuthentication no
PubkeyAuthentication yes
Port $SSH_PORT
EOF
sshd -t
systemctl reload ssh 2>/dev/null || systemctl reload sshd

echo "==> 3/6 Mises à jour de sécurité automatiques"
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y unattended-upgrades ufw fail2ban git ca-certificates curl gnupg
cat > /etc/apt/apt.conf.d/20auto-upgrades <<'EOF'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
EOF
systemctl enable --now unattended-upgrades

echo "==> 4/6 Pare-feu : SSH, HTTP, HTTPS uniquement"
ufw default deny incoming
ufw default allow outgoing
ufw allow "$SSH_PORT"/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 443/udp
ufw --force enable

echo "==> 5/6 Docker + Compose (dépôt officiel, versions figées par apt)"
. /etc/os-release
DISTRO="${ID:-debian}"
if [[ "$DISTRO" != "debian" && "$DISTRO" != "ubuntu" ]]; then
  echo "Distribution non gérée : installe Docker manuellement." >&2
  exit 1
fi
install -m 0755 -d /etc/apt/keyrings
curl -fsSL "https://download.docker.com/linux/${DISTRO}/gpg" -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/${DISTRO} ${VERSION_CODENAME} stable" \
  > /etc/apt/sources.list.d/docker.list
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
usermod -aG docker "$DEPLOY_USER"
systemctl enable --now docker

echo "==> 6/6 Répertoire applicatif"
install -d -m 750 -o "$DEPLOY_USER" -g "$DEPLOY_USER" /srv/portfolio-rag

cat <<EOF

Terminé. Étapes suivantes :
  1. Depuis TA machine : ssh-copy-id -p $SSH_PORT $DEPLOY_USER@SERVEUR
  2. Vérifie : ssh -p $SSH_PORT $DEPLOY_USER@SERVEUR
  3. Clone le dépôt dans /srv/portfolio-rag (voir docs/DEPLOYMENT.md)
  4. Contrôle depuis l'extérieur que seuls $SSH_PORT, 80 et 443 répondent.

Rappel : Docker publie ses ports en contournant ufw. Ici, seul Caddy publie
80/443 (docker-compose.prod.yml) ; postgres, chroma, airflow et l'API
n'exposent aucun port sur l'hôte.
EOF
