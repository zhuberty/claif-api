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
    --config "$CONFIG_FILE" || true

# Create the user with email verified and no required actions
/opt/bitnami/keycloak/bin/kcadm.sh create users -r "$KEYCLOAK_REALM" \
    -s username="$KEYCLOAK_USER_USERNAME" \
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
    -s clientAuthenticatorType="client-secret" \
    -s secret="$KEYCLOAK_CLIENT_SECRET" \
    -s 'redirectUris=["http://localhost/*"]' \
    -s 'webOrigins=["*"]' \
    -s publicClient=false \
    -s directAccessGrantsEnabled=true \
    -s serviceAccountsEnabled=true \
    --config "$CONFIG_FILE"
