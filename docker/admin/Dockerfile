FROM node:16-alpine as build

WORKDIR /app

# Installation des dépendances
COPY ./admin/package.json ./admin/package-lock.json* ./
RUN npm install

# Copie des fichiers sources
COPY ./admin .

# Construction de l'application
RUN npm run build

# Étape de production avec Nginx
FROM nginx:alpine

# Copie des fichiers de build
COPY --from=build /app/build /usr/share/nginx/html

# Copie de la configuration Nginx
COPY ./docker/admin/nginx.conf /etc/nginx/conf.d/default.conf

# Exposition du port
EXPOSE 3000

# Commande de démarrage
CMD ["nginx", "-g", "daemon off;"]
