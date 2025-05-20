# USSD Platform

Une plateforme USSD interne complète pour votre entreprise, hébergée sur votre propre serveur.

## Fonctionnalités

- Consultation de solde
- Inscription à des services
- Suivi de commande
- Sondages ou notifications
- Statistiques d'usage
- Interface d'administration web

## Architecture

- **Backend/API**: FastAPI (Python)
- **Base de données**: PostgreSQL
- **Déploiement**: Docker
- **Sécurité**: HTTPS avec Let's Encrypt
- **Monitoring**: Prometheus + Grafana

## Structure du Projet

```
ussd-platform/
├── api/                  # Code source de l'API FastAPI
│   ├── controllers/      # Contrôleurs pour les différentes routes
│   ├── models/           # Modèles de données
│   ├── services/         # Services métier
│   ├── utils/            # Utilitaires
│   └── main.py           # Point d'entrée de l'application
├── admin/                # Interface d'administration
├── db/                   # Scripts de migration et initialisation
├── docker/               # Fichiers Docker
├── docs/                 # Documentation
└── tests/                # Tests unitaires et d'intégration
```

## Prérequis

- Docker et Docker Compose
- Un serveur Ubuntu connecté à Internet
- Un agrégateur USSD ou une passerelle comme Kannel

## Installation

1. Cloner ce dépôt
2. Configurer les variables d'environnement dans le fichier `.env`
3. Lancer l'application avec Docker Compose:

```bash
docker-compose up -d
```

## Configuration

Créez un fichier `.env` à la racine du projet avec les variables suivantes:

```
DB_USER=ussd_user
DB_PASSWORD=your_secure_password
DB_NAME=ussd_db
DB_HOST=postgres
DB_PORT=5432
API_KEY=your_secure_api_key
ALLOWED_IPS=127.0.0.1,192.168.1.1
```

## Utilisation

### Exemple de flux USSD

1. L'utilisateur compose *123#
2. L'opérateur/agrégateur envoie la requête à /ussd
3. L'API répond: "CON Bienvenue\n1. Solde\n2. S'inscrire"
4. Si l'utilisateur tape 1, l'API retourne: "END Votre solde est de 10 000 FCFA"

## Sécurité

- Communication sécurisée via HTTPS
- Authentification par token API
- Liste blanche d'adresses IP
- Logs avec rotation automatique

## Maintenance

- Sauvegarde régulière de la base de données
- Mise à jour des dépendances
- Surveillance des logs et des métriques
