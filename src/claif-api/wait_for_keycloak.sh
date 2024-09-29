#!/bin/bash

set -e

host=$1
port="8080"
realm="fastapi"
timeout=300  # 5 minutes timeout
elapsed=0

echo "Waiting for Keycloak to start and realm to be populated..."

# Wait until Keycloak is up by checking the '/realms/master' endpoint
until curl -s http://$host:$port/realms/master > /dev/null; do
  echo "Waiting for Keycloak service at http://$host:$port/realms/master..."
  sleep 5
  elapsed=$((elapsed + 5))
  if [ $elapsed -ge $timeout ]; then
    echo "Timeout waiting for Keycloak service."
    exit 1
  fi
done

echo "Keycloak service is up!"

elapsed=0  # Reset the elapsed time for the next check

# Wait until the specific realm is available
until curl -s http://$host:$port/realms/$realm > /dev/null; do
  echo "Waiting for Keycloak realm '$realm' at http://$host:$port/realms/$realm..."
  sleep 5
  elapsed=$((elapsed + 5))
  if [ $elapsed -ge $timeout ]; then
    echo "Timeout waiting for Keycloak realm '$realm'."
    exit 1
  fi
done

echo "Keycloak is ready and the realm '$realm' is populated!"
