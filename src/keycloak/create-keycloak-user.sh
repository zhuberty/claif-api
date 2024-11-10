#!/bin/bash

CONFIG_FILE="/tmp/kcadm.config"

# Wait for Keycloak to start
until curl -s http://127.0.0.1:8080 > /dev/null; do
    echo "Waiting for Keycloak to start..."
    sleep 5
done

echo "Keycloak is up. Proceeding with configuration."

# Login to Keycloak
/opt/bitnami/keycloak/bin/kcadm.sh config credentials \
    --server http://127.0.0.1:8080 \
    --realm master \
    --user "$KEYCLOAK_ADMIN" \
    --password "$KEYCLOAK_ADMIN_PASSWORD" \
    --config "$CONFIG_FILE"

# Create the realm if it doesn't exist
/opt/bitnami/keycloak/bin/kcadm.sh create realms \
    -s realm="$KEYCLOAK_REALM" \
    -s enabled=true \
    -s 'accessTokenLifespan=1800' \
    -s 'accessTokenLifespanForImplicitFlow=1800' \
    --config "$CONFIG_FILE" || true

# Create the user with email verified and no required actions
/opt/bitnami/keycloak/bin/kcadm.sh create users -r "$KEYCLOAK_REALM" \
    -s username="$KEYCLOAK_USER_USERNAME" \
    -s firstName="$KEYCLOAK_USER_FIRST_NAME" \
    -s lastName="$KEYCLOAK_USER_LAST_NAME" \
    -s enabled=true \
    -s email="$KEYCLOAK_USER_EMAIL" \
    -s emailVerified=true \
    -s requiredActions=[] \
    --config "$CONFIG_FILE"

# Set the user's password as non-temporary
/opt/bitnami/keycloak/bin/kcadm.sh set-password -r "$KEYCLOAK_REALM" \
    --username "$KEYCLOAK_USER_USERNAME" \
    --new-password "$KEYCLOAK_USER_PASSWORD" \
    --temporary=false \
    --config "$CONFIG_FILE"

# Create the client
/opt/bitnami/keycloak/bin/kcadm.sh create clients -r "$KEYCLOAK_REALM" \
    -s clientId="$KEYCLOAK_CLIENT_ID" \
    -s enabled=true \
    -s protocol="openid-connect" \
    -s 'redirectUris=["http://localhost/*"]' \
    -s 'webOrigins=["*"]' \
    -s publicClient=true \
    -s directAccessGrantsEnabled=true \
    --config "$CONFIG_FILE"

create-keycloak-user.sh: |
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
KEYCLOAK_ADMIN=${KEYCLOAK_ADMIN:-"admin"}
KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASSWORD:-"admin-password"}
KEYCLOAK_REALM=${KEYCLOAK_REALM:-"master"}
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
    --user "$KEYCLOAK_ADMIN" \
    --password "$KEYCLOAK_ADMIN_PASSWORD" \
    --config "$CONFIG_FILE"

# Create the user
/opt/bitnami/keycloak/bin/kcadm.sh create users -r "$KEYCLOAK_REALM" \
    -s username="$USERNAME" \
    -s firstName="$FIRST_NAME" \
    -s lastName="$LAST_NAME" \
    -s enabled=true \
    -s email="$EMAIL" \
    -s emailVerified=true \
    --config "$CONFIG_FILE"

# Set the user's password as non-temporary
/opt/bitnami/keycloak/bin/kcadm.sh set-password -r "$KEYCLOAK_REALM" \
    --username "$USERNAME" \
    --new-password "$PASSWORD" \
    --temporary=false \
    --config "$CONFIG_FILE"

echo "User $USERNAME created successfully."