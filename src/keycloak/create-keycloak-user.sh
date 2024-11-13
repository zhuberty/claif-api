#!/bin/bash

# Ensure all required arguments are provided
if [[ $# -ne 5 ]]; then
    echo "Usage: $0 <USERNAME> <FIRST_NAME> <LAST_NAME> <EMAIL> <PASSWORD>"
    exit 1
fi

# Extract arguments
USERNAME=$(echo "$1" | tr '[:upper:]' '[:lower:]') # Convert to lowercase
FIRST_NAME="$2"
LAST_NAME="$3"
EMAIL="$4"
PASSWORD="$5"

# Load environment variables already set in the Keycloak container
CONFIG_FILE="/tmp/kcadm.config"

# Wait for Keycloak to be up
until curl -s http://127.0.0.1:8080 > /dev/null; do
    echo "Waiting for Keycloak to start..."
    sleep 5
done

echo "Keycloak is up. Proceeding with user creation."

# Login to Keycloak
/opt/bitnami/keycloak/bin/kcadm.sh config credentials \
    --server http://127.0.0.1:8080 \
    --realm master \
    --user "$KC_BOOTSTRAP_ADMIN_USERNAME" \
    --password "$KC_BOOTSTRAP_ADMIN_PASSWORD" \
    --config "$CONFIG_FILE"

# Check if the user already exists
USER_EXISTS=$(/opt/bitnami/keycloak/bin/kcadm.sh get users -r "$KEYCLOAK_REALM" \
    -q username="$USERNAME" \
    --config "$CONFIG_FILE" | grep -c "\"username\"")

if [[ "$USER_EXISTS" -gt 0 ]]; then
    echo "User $USERNAME already exists. Skipping creation."
else
    # Create the user
    /opt/bitnami/keycloak/bin/kcadm.sh create users -r "$KEYCLOAK_REALM" \
        -s username="$USERNAME" \
        -s firstName="$FIRST_NAME" \
        -s lastName="$LAST_NAME" \
        -s enabled=true \
        -s email="$EMAIL" \
        -s emailVerified=true \
        --config "$CONFIG_FILE"

    echo "User $USERNAME created successfully."
fi

# Set the user's password as non-temporary only if the user exists
/opt/bitnami/keycloak/bin/kcadm.sh set-password -r "$KEYCLOAK_REALM" \
    --username "$USERNAME" \
    --new-password "$PASSWORD" \
    --temporary=false \
    --config "$CONFIG_FILE"

echo "Password for $USERNAME has been set successfully."
