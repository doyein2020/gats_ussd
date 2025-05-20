#!/bin/bash

# Créer le répertoire pour les certificats s'il n'existe pas
mkdir -p /etc/nginx/ssl

# Générer une clé privée
openssl genrsa -out /etc/nginx/ssl/privkey.pem 2048

# Générer un certificat auto-signé valide pour 10 ans
openssl req -new -x509 -key /etc/nginx/ssl/privkey.pem -out /etc/nginx/ssl/fullchain.pem -days 3650 -subj "/C=FR/ST=State/L=City/O=Organization/CN=localhost"

# Générer les paramètres Diffie-Hellman
openssl dhparam -out /etc/nginx/ssl/dhparam.pem 2048

# Créer un fichier d'options SSL
cat > /etc/nginx/ssl/options-ssl-nginx.conf << 'EOL'
ssl_session_cache shared:le_nginx_SSL:10m;
ssl_session_timeout 1440m;
ssl_session_tickets off;

ssl_protocols TLSv1.2 TLSv1.3;
ssl_prefer_server_ciphers on;
ssl_ciphers "ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384";

ssl_stapling off;
ssl_stapling_verify off;
EOL

echo "Certificat auto-signé généré avec succès"
