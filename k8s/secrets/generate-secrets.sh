#!/bin/bash

# Check if namespace parameter is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <namespace>"
  exit 1
fi

NAMESPACE="$1"

# Define the secret names
CLAIF_API_SECRET_NAME="claif-api-secrets"
CLAIF_DB_SECRET_NAME="claif-db-secrets"
KEYCLOAK_SECRET_NAME="keycloak-secrets"
KEYCLOAK_DB_SECRET_NAME="keycloak-db-secrets"
MINIO_SECRET_NAME="minio-secrets"

# Define the secrets for each group
declare -A CLAIF_API_SECRETS=(
  [UVICORN_WORKERS]="1"
  [DATABASE_URL]="claif-db"
  [CLAIF_API_HOST]="claif-api"
  [CLAIF_API_PORT]="8000"
)

declare -A CLAIF_DB_SECRETS=(
  [CLAIF_DB_USER]="postgres"
  [CLAIF_DB_PASSWORD]=""
  [CLAIF_DB_DATABASE]=""
  [NEW_DB_USER]=""
  [NEW_DB_PASSWORD]=""
  [NEW_DB_NAME]=""
)

declare -A KEYCLOAK_SECRETS=(
  [KEYCLOAK_REALM]=""
  [KEYCLOAK_CLIENT_ID]=""
  [KEYCLOAK_CLIENT_SECRET]=""
  [KEYCLOAK_CREATE_ADMIN_USER]="true"
  [KEYCLOAK_ADMIN]=""
  [KEYCLOAK_ADMIN_PASSWORD]=""
  [KEYCLOAK_USER_USERNAME]=""
  [KEYCLOAK_USER_FIRST_NAME]=""
  [KEYCLOAK_USER_LAST_NAME]=""
  [KEYCLOAK_USER_EMAIL]="keycloak-user@claif.org"
  [KEYCLOAK_USER_PASSWORD]=""
  [KEYCLOAK_SERVER_URL]="http://keycloak:8080"
)

declare -A KEYCLOAK_DB_SECRETS=(
  [KEYCLOAK_DB_USERNAME]=""
  [KEYCLOAK_DB_PASSWORD]=""
  [KEYCLOAK_DB_DATABASE]=""
)

declare -A MINIO_SECRETS=(
  [MINIO_ACCESS_KEY]=""
  [MINIO_SECRET_KEY]=""
)

# Function to generate safe random strings
generate_safe_random_string() {
  local LENGTH=${1:-32}
  tr -dc 'A-Za-z0-9' </dev/urandom | head -c ${LENGTH}
}

generate_secrets() {
  local -n SECRET_KEYS=$1
  local SECRET_NAME=$2

  # Loop through each secret key
  for KEY in "${!SECRET_KEYS[@]}"; do
    # Use default value if set, otherwise generate a random value
    if [ -n "${SECRET_KEYS[$KEY]}" ]; then
      # Default value is already set in the array, use it as is
      :
    else
      # Generate a random value
      SECRET_KEYS[$KEY]="$(generate_safe_random_string)"
    fi

    # Convert KEYCLOAK_USER_USERNAME to lowercase if it exists
    if [ "$KEY" == "KEYCLOAK_USER_USERNAME" ]; then
      SECRET_KEYS[$KEY]=$(echo "${SECRET_KEYS[$KEY]}" | tr '[:upper:]' '[:lower:]')
    fi
  done

  # Create a temporary file to hold the Kubernetes secret YAML
  TMP_SECRET_FILE=$(mktemp)

  # Start constructing the YAML
  cat <<EOF > $TMP_SECRET_FILE
apiVersion: v1
kind: Secret
metadata:
  name: $SECRET_NAME
  namespace: $NAMESPACE
type: Opaque
data:
EOF

  # Add each secret key-value pair to the YAML, base64 encoded
  for KEY in "${!SECRET_KEYS[@]}"; do
    VALUE=$(echo -n "${SECRET_KEYS[$KEY]}" | base64)
    echo "  ${KEY}: ${VALUE}" >> $TMP_SECRET_FILE
  done

  # Apply the secret to Kubernetes
  kubectl apply -f $TMP_SECRET_FILE

  # Clean up
  rm $TMP_SECRET_FILE

  echo "Secret '$SECRET_NAME' has been generated and applied successfully."
}

# Generate secrets for each group
generate_secrets CLAIF_API_SECRETS $CLAIF_API_SECRET_NAME
generate_secrets CLAIF_DB_SECRETS $CLAIF_DB_SECRET_NAME
generate_secrets KEYCLOAK_SECRETS $KEYCLOAK_SECRET_NAME
generate_secrets KEYCLOAK_DB_SECRETS $KEYCLOAK_DB_SECRET_NAME
generate_secrets MINIO_SECRETS $MINIO_SECRET_NAME
