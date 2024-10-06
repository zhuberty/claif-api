#!/bin/bash

set -e

host=$1
port="8080"
realm="fastapi"
timeout=300  # 5 minutes timeout
elapsed=0

log() {
    echo -e "wait_for_keycloak.sh:$1:\t$2"
}

log INFO "Waiting for Keycloak to start and realm to be populated..."

# Wait until Keycloak is up by checking the '/realms/master' endpoint
until curl -s http://$host:$port/realms/master > /dev/null; do
  log INFO "Waiting for Keycloak service at http://$host:$port/realms/master..."
  sleep 5
  elapsed=$((elapsed + 5))
  if [ $elapsed -ge $timeout ]; then
    log ERROR "Timeout waiting for Keycloak service."
    exit 1
  fi
done

log INFO "Keycloak service is up!"

elapsed=0  # Reset the elapsed time for the next check

# Wait until the specific realm is available
until curl -s http://$host:$port/realms/$realm > /dev/null; do
  log INFO "Waiting for Keycloak realm '$realm' at http://$host:$port/realms/$realm..."
  sleep 5
  elapsed=$((elapsed + 5))
  if [ $elapsed -ge $timeout ]; then
    log ERROR "Timeout waiting for Keycloak realm '$realm'."
    exit 1
  fi
done

log INFO "Keycloak is ready and the realm '$realm' is populated!"
