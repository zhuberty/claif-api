#!/bin/bash

# Check if a namespace is provided as an argument
if [ -z "$1" ]; then
  echo "Usage: $0 <namespace>"
  exit 1
fi

NAMESPACE=$1
BACKUP_DIR="$HOME/.claif-secrets/$NAMESPACE"

# Create the backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

echo "Fetching secrets from namespace: $NAMESPACE"
echo "Secrets will be saved in: $BACKUP_DIR"

# Get the list of secrets in the namespace
SECRETS=$(kubectl get secrets -n "$NAMESPACE" -o jsonpath='{.items[*].metadata.name}')

if [ -z "$SECRETS" ]; then
  echo "No secrets found in namespace $NAMESPACE."
  exit 0
fi

# Iterate over each secret
for SECRET_NAME in $SECRETS; do
  SECRET_FILE="$BACKUP_DIR/$SECRET_NAME.yaml"
  echo "Processing secret: $SECRET_NAME"

  # Fetch the secret and decode the values
  kubectl get secret "$SECRET_NAME" -n "$NAMESPACE" -o json | jq -r 'del(.metadata.managedFields) | .data | to_entries[] | .key as $key | "\($key): " + (.value | @base64d)' > "$SECRET_FILE"

  if [ $? -eq 0 ]; then
    echo "Decoded secret saved to: $SECRET_FILE"
  else
    echo "Failed to decode secret: $SECRET_NAME"
  fi
done

echo "All secrets have been backed up to: $BACKUP_DIR"
