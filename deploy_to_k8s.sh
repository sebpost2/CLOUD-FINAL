#!/bin/bash

kubectl apply -f kubernetes/backend-deployment.yaml
kubectl apply -f kubernetes/frontend-deployment.yaml
kubectl apply -f kubernetes/ingress.yaml
kubectl apply -f kubernetes/pvc.yaml
kubectl apply -f kubernetes/backend-hpa.yaml
kubectl apply -f kubernetes/frontend-hpa.yaml
