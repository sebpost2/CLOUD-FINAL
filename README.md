# Proyecto de Buscador de Videos con Etiquetado Avanzado y Kubernetes

Este proyecto es una aplicación web que permite subir videos, procesarlos para obtener etiquetas detalladas (como "carro verde en la calle"), buscar videos basados en esas etiquetas y reproducirlos con controles avanzados. La aplicación utiliza modelos de aprendizaje automático para el etiquetado y está diseñada para ser desplegada en Kubernetes, permitiendo el autoescalado basado en la carga.

## Tabla de Contenidos

- [Características](#características)
- [Requisitos Previos](#requisitos-previos)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Instrucciones de Instalación y Ejecución](#instrucciones-de-instalación-y-ejecución)
  - [1. Clonar el Repositorio](#1-clonar-el-repositorio)
  - [2. Configurar el Directorio de Modelos](#2-configurar-el-directorio-de-modelos)
  - [3. Configurar Docker](#3-configurar-docker)
  - [4. Construir y Publicar Imágenes Docker](#4-construir-y-publicar-imágenes-docker)
  - [5. Configurar Kubernetes](#5-configurar-kubernetes)
  - [6. Desplegar la Aplicación en Kubernetes](#6-desplegar-la-aplicación-en-kubernetes)
  - [7. Probar la Aplicación](#7-probar-la-aplicación)
  - [8. Detener Minikube](#8-detener-minikube)
- [Archivos de Configuración](#archivos-de-configuración)
- [Scripts Útiles](#scripts-útiles)
- [Personalización](#personalización)
- [Notas y Consideraciones](#notas-y-consideraciones)
- [Cómo Probar el Código Nuevamente](#cómo-probar-el-código-nuevamente)

---

## Características

- **Etiquetado Avanzado**: Utiliza YOLOv5 para detección de objetos, detección de colores y BLIP para descripciones detalladas.
- **Interfaz de Usuario**: Frontend web que permite subir, buscar y reproducir videos con controles avanzados.
- **Backend API**: Construida con Flask, proporciona endpoints para subir, procesar y buscar videos.
- **Despliegue en Kubernetes**: Configuración para desplegar en Kubernetes con autoescalado basado en la carga.
- **Autoescalado**: Configurado para escalar automáticamente pods y nodos en función de la carga de CPU.

## Requisitos Previos

- **Docker** instalado en tu máquina local.
- **Minikube** para pruebas locales de Kubernetes.
- **kubectl** configurado para interactuar con tu clúster.
- **Cuenta en Docker Hub** (o en otro registro de imágenes) para publicar las imágenes Docker.
- **Python 3.8** o superior.
- **Git** instalado en tu sistema.

## Estructura del Proyecto

```
proyecto/
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── ... (otros archivos del backend)
├── frontend/
│   ├── index.html
│   ├── Dockerfile
│   └── ... (otros archivos del frontend)
├── models/
│   └── yolov5/ (Código de YOLOv5)
├── kubernetes/
│   ├── backend-deployment.yaml
│   ├── frontend-deployment.yaml
│   ├── ingress.yaml
│   ├── pvc.yaml
│   ├── backend-hpa.yaml
│   └── frontend-hpa.yaml
├── build_and_push.sh
└── deploy_to_k8s.sh
```

---

## Instrucciones de Instalación y Ejecución

### **1. Clonar el Repositorio**

Clona este repositorio en tu máquina local:

```bash
git clone https://github.com/tu_usuario/proyecto.git
cd proyecto
```

### **2. Configurar el Directorio de Modelos**

Crea un directorio llamado `models` en la raíz del proyecto y descarga YOLOv5 dentro de él:

```bash
mkdir models
cd models
git clone https://github.com/ultralytics/yolov5.git
cd ..
```

Esto descargará el código de YOLOv5 en `models/yolov5`. Asegúrate de que la estructura de carpetas sea correcta para que el backend pueda encontrar los modelos.

### **3. Configurar Docker**

Asegúrate de tener Docker instalado y funcionando:

```bash
docker --version
```

Si no lo tienes instalado, puedes descargarlo desde [Docker Desktop](https://www.docker.com/products/docker-desktop).

Inicia sesión en Docker Hub:

```bash
docker login
```

### **4. Construir y Publicar Imágenes Docker**

Antes de construir las imágenes, reemplaza `tu_usuario` con tu nombre de usuario en Docker Hub en los archivos `build_and_push.sh` y los `Dockerfile`.

#### **a. Modificar los `Dockerfile`**

**Backend (`backend/Dockerfile`):**

```dockerfile
# Dockerfile para el Backend
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Copiar el directorio de modelos
COPY ../models /app/models

EXPOSE 5000

CMD ["python", "app.py"]
```

**Frontend (`frontend/Dockerfile`):**

```dockerfile
# Dockerfile para el Frontend
FROM nginx:alpine

COPY index.html /usr/share/nginx/html/index.html
```

#### **b. Modificar `build_and_push.sh`**

```bash
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
```

Haz el archivo ejecutable:

```bash
chmod +x build_and_push.sh
```

#### **c. Ejecutar el Script de Construcción y Publicación**

Ejecuta el script para construir y publicar las imágenes:

```bash
./build_and_push.sh
```

### **5. Configurar Kubernetes**

Asegúrate de tener Minikube y kubectl instalados y configurados:

- **Instalar Minikube**: [Guía de instalación](https://minikube.sigs.k8s.io/docs/start/)
- **Instalar kubectl**: [Guía de instalación](https://kubernetes.io/docs/tasks/tools/)

Inicia Minikube:

```bash
minikube start
```

### **6. Desplegar la Aplicación en Kubernetes**

Antes de desplegar, edita los archivos YAML para reemplazar `tu_usuario` con tu nombre de usuario de Docker Hub.

#### **a. Modificar `backend-deployment.yaml` y `frontend-deployment.yaml`**

En ambos archivos, busca las líneas que especifican la imagen y reemplaza `tu_usuario`:

```yaml
image: tu_usuario/video-backend:latest
```

#### **b. Aplicar las Configuraciones de Kubernetes**

Ejecuta el script `deploy_to_k8s.sh`:

```bash
./deploy_to_k8s.sh
```

El contenido de `deploy_to_k8s.sh` es:

```bash
#!/bin/bash

kubectl apply -f kubernetes/pvc.yaml
kubectl apply -f kubernetes/backend-deployment.yaml
kubectl apply -f kubernetes/frontend-deployment.yaml
kubectl apply -f kubernetes/ingress.yaml
kubectl apply -f kubernetes/backend-hpa.yaml
kubectl apply -f kubernetes/frontend-hpa.yaml
```

Haz el archivo ejecutable:

```bash
chmod +x deploy_to_k8s.sh
```

### **7. Probar la Aplicación**

#### **a. Obtener la IP de Minikube**

```bash
minikube ip
```

Supongamos que la IP es `192.168.99.100`.

#### **b. Configurar el Archivo `index.html`**

Edita `frontend/index.html` y actualiza la variable `apiBaseUrl` para apuntar al servicio del backend:

```javascript
const apiBaseUrl = 'http://192.168.99.100:30001';
```

Reconstruye y publica la imagen del frontend:

```bash
cd frontend
docker build -t tu_usuario/video-frontend:latest .
docker push $DOCKER_USER/video-frontend:latest
cd ..
```

Aplica nuevamente el despliegue del frontend:

```bash
kubectl apply -f kubernetes/frontend-deployment.yaml
```

#### **c. Acceder a la Aplicación**

Abre tu navegador y visita:

```
http://192.168.99.100:30002
```

Ahora puedes:

- **Subir Videos**: Usa el formulario para subir un video desde tu computadora.
- **Buscar Videos**: Ingresa una consulta en la barra de búsqueda y presiona "Buscar".
- **Reproducir Videos**: Selecciona un video de los resultados y utiliza los controles del reproductor.

### **8. Detener Minikube**

Cuando hayas terminado, detén Minikube para liberar recursos:

```bash
minikube stop
```

---

## Archivos de Configuración

Los archivos de configuración importantes incluyen:

- `backend/Dockerfile`
- `frontend/Dockerfile`
- `backend/requirements.txt`
- `kubernetes/backend-deployment.yaml`
- `kubernetes/frontend-deployment.yaml`
- `kubernetes/ingress.yaml`
- `kubernetes/pvc.yaml`
- `kubernetes/backend-hpa.yaml`
- `kubernetes/frontend-hpa.yaml`

Asegúrate de revisar y modificar estos archivos según tus necesidades.

---

## Scripts Útiles

### **`build_and_push.sh`**

```bash
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
```

### **`deploy_to_k8s.sh`**

```bash
#!/bin/bash

kubectl apply -f kubernetes/pvc.yaml
kubectl apply -f kubernetes/backend-deployment.yaml
kubectl apply -f kubernetes/frontend-deployment.yaml
kubectl apply -f kubernetes/ingress.yaml
kubectl apply -f kubernetes/backend-hpa.yaml
kubectl apply -f kubernetes/frontend-hpa.yaml
```

---

## Personalización

- **Nombre de Usuario de Docker Hub**: Reemplaza `tu_usuario` en los archivos `Dockerfile`, `build_and_push.sh`, y los archivos YAML de Kubernetes con tu nombre de usuario.
- **Configuración de Recursos**: Ajusta las solicitudes y límites de CPU y memoria en los despliegues según tus necesidades.
- **Variables de Entorno**: Si necesitas agregar variables de entorno, puedes hacerlo en los archivos de despliegue bajo `env`.

---

## Notas y Consideraciones

- **Descarga de Modelos**: Al iniciar la aplicación por primera vez, los modelos de BLIP y otros pueden descargarse automáticamente. Asegúrate de que tu entorno tiene acceso a Internet.
- **Persistencia de Datos**: En este ejemplo, se utiliza `emptyDir` para el almacenamiento de videos, lo cual es temporal. Para almacenamiento persistente, configura un `PersistentVolume` y un `PersistentVolumeClaim`.
- **Autoescalado de Nodos**: Minikube no soporta autoescalado de nodos. Para pruebas de autoescalado de nodos, utiliza un proveedor de nube como GKE, EKS o AKS.
- **Seguridad**: Este ejemplo no incluye autenticación ni HTTPS. Para producción, implementa medidas de seguridad adecuadas.
- **Monitoreo**: Considera agregar herramientas de monitoreo como Prometheus y Grafana para supervisar el rendimiento.
- **Compatibilidad**: Asegúrate de que todas las versiones de las dependencias son compatibles. Puedes usar entornos virtuales para aislar las dependencias.

---

## Cómo Probar el Código Nuevamente

Si deseas probar el código nuevamente:

1. **Detén Minikube si está corriendo**:

   ```bash
   minikube stop
   ```

2. **Inicia Minikube**:

   ```bash
   minikube start
   ```

3. **Reconstruye y publica las imágenes Docker**:

   ```bash
   ./build_and_push.sh
   ```

4. **Despliega la aplicación en Kubernetes**:

   ```bash
   ./deploy_to_k8s.sh
   ```

5. **Obtén la IP de Minikube y actualiza `index.html` si es necesario**:

   ```bash
   minikube ip
   ```

6. **Accede a la aplicación en tu navegador**:

   ```
   http://<ip-minikube>:30002
   ```

7. **Prueba las funcionalidades**:

   - **Subir Videos**
   - **Buscar Videos**
   - **Reproducir Videos**

8. **Detén Minikube cuando hayas terminado**:

   ```bash
   minikube stop
   ```

---

¡Ahora estás listo para ejecutar y probar la aplicación desde cero! Si tienes alguna pregunta o encuentras algún problema, no dudes en consultarme. ¡Buena suerte!
