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
    --user "$KC_BOOTSTRAP_ADMIN_USERNAME" \
    --password "$KC_BOOTSTRAP_ADMIN_PASSWORD" \
    --config "$CONFIG_FILE"

# Check if the realm exists, create if it doesn't
if ! /opt/bitnami/keycloak/bin/kcadm.sh get realms/"$KEYCLOAK_REALM" --config "$CONFIG_FILE" > /dev/null 2>&1; then
    echo "Creating realm: $KEYCLOAK_REALM"
    /opt/bitnami/keycloak/bin/kcadm.sh create realms \
        -s realm="$KEYCLOAK_REALM" \
        -s enabled=true \
        -s 'accessTokenLifespan=1800' \
        -s 'accessTokenLifespanForImplicitFlow=1800' \
        --config "$CONFIG_FILE"
else
    echo "Realm $KEYCLOAK_REALM already exists."
fi

# Check if the user exists, create if it doesn't
if ! /opt/bitnami/keycloak/bin/kcadm.sh get users -r "$KEYCLOAK_REALM" -q username="$KEYCLOAK_USER_USERNAME" --config "$CONFIG_FILE" | grep -q '"username"'; then
    echo "Creating user: $KEYCLOAK_USER_USERNAME"
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
else
    echo "User $KEYCLOAK_USER_USERNAME already exists."
fi

# Check if the client exists, create if it doesn't
if ! /opt/bitnami/keycloak/bin/kcadm.sh get clients -r "$KEYCLOAK_REALM" -q clientId="$KEYCLOAK_CLIENT_ID" --config "$CONFIG_FILE" | grep -q '"clientId"'; then
    echo "Creating client: $KEYCLOAK_CLIENT_ID"
    /opt/bitnami/keycloak/bin/kcadm.sh create clients -r "$KEYCLOAK_REALM" \
        -s clientId="$KEYCLOAK_CLIENT_ID" \
        -s enabled=true \
        -s protocol="openid-connect" \
        -s 'redirectUris=["http://localhost/*"]' \
        -s 'webOrigins=["*"]' \
        -s publicClient=true \
        -s directAccessGrantsEnabled=true \
        --config "$CONFIG_FILE"
else
    echo "Client $KEYCLOAK_CLIENT_ID already exists."
fi
