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

# Define the secrets for each group
declare -A CLAIF_API_SECRETS=(
  [UVICORN_WORKERS]=""
  [APP_MODULE]=""
  [DATABASE_URL]=""
  [KEYCLOAK_SERVER_URL]=""
  [KEYCLOAK_REALM]=""
  [KEYCLOAK_CLIENT_ID]=""
  [KEYCLOAK_CLIENT_SECRET]=""
  [CLAIF_API_HOST]=""
  [CLAIF_API_PORT]=""
)

declare -A CLAIF_DB_SECRETS=(
  [POSTGRESQL_USERNAME]=""
  [POSTGRESQL_PASSWORD]=""
  [POSTGRESQL_DATABASE]=""
)

declare -A KEYCLOAK_SECRETS=(
  [KEYCLOAK_CREATE_ADMIN_USER]=""
  [KEYCLOAK_ADMIN]=""
  [KEYCLOAK_ADMIN_PASSWORD]=""
  [KEYCLOAK_REALM]=""
  [KEYCLOAK_USER_USERNAME]=""
  [KEYCLOAK_USER_FIRST_NAME]=""
  [KEYCLOAK_USER_LAST_NAME]=""
  [KEYCLOAK_USER_EMAIL]=""
  [KEYCLOAK_USER_PASSWORD]=""
  [KEYCLOAK_CLIENT_ID]=""
  [KEYCLOAK_CLIENT_SECRET]=""
)

declare -A KEYCLOAK_DB_SECRETS=(
  [POSTGRESQL_USERNAME]=""
  [POSTGRESQL_PASSWORD]=""
  [POSTGRESQL_DATABASE]=""
)

# Function to generate secrets
generate_secrets() {
  local -n SECRET_KEYS=$1
  local SECRET_NAME=$2

  # Loop through each secret key
  for KEY in "${!SECRET_KEYS[@]}"; do
    # Construct the environment variable name (e.g., CLAIFSEC_KEYCLOAK_ADMIN)
    ENV_VAR="CLAIFSEC_${KEY}"

    # Check if the environment variable is set
    if [ -n "${!ENV_VAR}" ]; then
      SECRET_KEYS[$KEY]="${!ENV_VAR}"
    else
      # Generate a random value if not set
      SECRET_KEYS[$KEY]="$(openssl rand -base64 32)"
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
