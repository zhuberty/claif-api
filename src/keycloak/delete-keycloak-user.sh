#!/bin/bash

# Ensure the username is provided
if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <USERNAME>"
    exit 1
fi

USERNAME=$(echo "$1" | tr '[:upper:]' '[:lower:]') # Convert to lowercase

# Load environment variables already set in the Keycloak container
CONFIG_FILE="/tmp/kcadm.config"

# Wait for Keycloak to be up
until curl -s http://127.0.0.1:8080 > /dev/null; do
    echo "Waiting for Keycloak to start..."
    sleep 5
done

echo "Keycloak is up. Proceeding with user deletion."

# Login to Keycloak
/opt/bitnami/keycloak/bin/kcadm.sh config credentials \
    --server http://127.0.0.1:8080 \
    --realm master \
    --user "$KC_BOOTSTRAP_ADMIN_USERNAME" \
    --password "$KC_BOOTSTRAP_ADMIN_PASSWORD" \
    --config "$CONFIG_FILE"

# Get the user ID
USER_JSON=$(/opt/bitnami/keycloak/bin/kcadm.sh get users -r "$KEYCLOAK_REALM" \
    -q username="$USERNAME" \
    --config "$CONFIG_FILE")

USER_ID=$(echo "$USER_JSON" | grep -o '"id"[[:space:]]*:[[:space:]]*"[a-f0-9-]*"' | head -n1 | sed 's/.*"id"[[:space:]]*:[[:space:]]*"\([a-f0-9-]*\)".*/\1/')

if [[ -z "$USER_ID" ]]; then
    echo "User $USERNAME not found."
    exit 1
fi

# Delete the user
/opt/bitnami/keycloak/bin/kcadm.sh delete users/"$USER_ID" -r "$KEYCLOAK_REALM" \
    --config "$CONFIG_FILE"

echo "User $USERNAME deleted successfully."