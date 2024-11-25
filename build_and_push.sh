#!/bin/bash

# Reemplaza 'tu_usuario' con tu nombre de usuario de Docker Hub
DOCKER_USER="tu_usuario"

# Construir y publicar la imagen del backend
cd backend
docker build -t $DOCKER_USER/video-backend:latest .
docker push $DOCKER_USER/video-backend:latest
cd ..

# Construir y publicar la imagen del frontend
cd frontend
docker build -t $DOCKER_USER/video-frontend:latest .
docker push $DOCKER_USER/video-frontend:latest
cd ..
