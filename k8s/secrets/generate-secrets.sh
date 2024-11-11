#!/bin/bash

# Function to display usage
usage() {
  echo "Usage: $0 <namespace> [--cert <path_to_cert>] [--key <path_to_key>]"
  echo "  If --cert and --key are supplied, the TLS secret will be created."
  exit 1
}

# Check if namespace parameter is provided
if [ -z "$1" ]; then
  usage
fi

# Parse the namespace argument
NAMESPACE="$1"
shift

# Initialize TLS cert and key variables
TLS_CERT=""
TLS_KEY=""

# Parse optional arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --cert)
      TLS_CERT="$2"
      shift 2
      ;;
    --key)
      TLS_KEY="$2"
      shift 2
      ;;
    *)
      echo "Unknown parameter: $1"
      usage
      ;;
  esac
done

# If either TLS_CERT or TLS_KEY is supplied, ensure both are supplied
if [[ -n "$TLS_CERT" ]] || [[ -n "$TLS_KEY" ]]; then
  if [[ -z "$TLS_CERT" ]] || [[ -z "$TLS_KEY" ]]; then
    echo "Error: Both --cert and --key must be specified together."
    usage
  fi

  # Check if cert and key files exist
  if [[ ! -f "$TLS_CERT" ]]; then
    echo "Error: Certificate file '$TLS_CERT' does not exist."
    exit 1
  fi

  if [[ ! -f "$TLS_KEY" ]]; then
    echo "Error: Key file '$TLS_KEY' does not exist."
    exit 1
  fi

  CREATE_TLS_SECRET=true
else
  CREATE_TLS_SECRET=false
fi

# Define the secret names
CLAIF_API_SECRET_NAME="claif-api-secrets"
CLAIF_DB_SECRET_NAME="claif-db-secrets"
KEYCLOAK_SECRET_NAME="keycloak-secrets"
KEYCLOAK_DB_SECRET_NAME="keycloak-db-secrets"
MINIO_SECRET_NAME="minio-secrets"
KEYCLOAK_TLS_SECRET_NAME="keycloak-tls-secret"

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
  [MINIO_ROOT_USER]=""
  [MINIO_ROOT_PASSWORD]=""
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

# If CREATE_TLS_SECRET is true, create the TLS secret
if [ "$CREATE_TLS_SECRET" = true ]; then
  # Read and base64-encode the cert and key files
  TLS_CRT_BASE64=$(base64 -w 0 "$TLS_CERT")
  TLS_KEY_BASE64=$(base64 -w 0 "$TLS_KEY")

  # Create a temporary file to hold the Kubernetes secret YAML
  TMP_TLS_SECRET_FILE=$(mktemp)

  # Generate the secret YAML
  cat <<EOF > $TMP_TLS_SECRET_FILE
apiVersion: v1
kind: Secret
metadata:
  name: $KEYCLOAK_TLS_SECRET_NAME
  namespace: $NAMESPACE
type: kubernetes.io/tls
data:
  tls.crt: $TLS_CRT_BASE64
  tls.key: $TLS_KEY_BASE64
EOF

  # Apply the secret to Kubernetes
  kubectl apply -f $TMP_TLS_SECRET_FILE

  # Clean up
  rm $TMP_TLS_SECRET_FILE

  echo "TLS Secret '$KEYCLOAK_TLS_SECRET_NAME' has been generated and applied successfully."
fi
