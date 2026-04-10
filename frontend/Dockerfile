# Stage 1: Build the React Application
FROM node:18-alpine AS builder

WORKDIR /app

# Copying package definitions independently caches Node Modules install layers efficiently
COPY package.json package-lock.json* ./
RUN npm install

# Bundle app source and execute Vite production build
COPY . .
RUN npm run build

# Stage 2: Serve using Nginx
FROM nginx:alpine

# Purge default nginx configurations natively
RUN rm -rf /usr/share/nginx/html/*

# Relocate built Vite static files 
COPY --from=builder /app/dist /usr/share/nginx/html

# Replace Default Router Config binding standard SPA fallbacks
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
