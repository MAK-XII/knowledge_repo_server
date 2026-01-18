#!/bin/bash


set -e

echo "Creating secrets for knowledge-repo namespace..."

read -sp "Enter DATABASE_URL: " DATABASE_URL
echo
read -sp "Enter JWT_SECRET: " JWT_SECRET
echo

kubectl create secret generic app-secrets \
  --from-literal=DATABASE_URL="$DATABASE_URL" \
  --from-literal=JWT_SECRET="$JWT_SECRET" \
  -n knowledge-repo \
  --dry-run=client -o yaml | kubectl apply -f -

echo " Secrets created successfully!"
echo ""
echo "To verify:"
echo "  kubectl get secret app-secrets -n knowledge-repo"