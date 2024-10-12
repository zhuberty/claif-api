#!/usr/bin/env bash
set -e

TIMEOUT=300  # 5 minutes timeout
QUIET=0
HOST=""
PORT="9000"  # Default MinIO port

log() { if [ "$QUIET" -ne 1 ]; then echo -e "wait_for_minio.sh:$1:\t$2" 1>&2; fi }

usage() {
    echo "Usage: $0 host:port [-t timeout] [-- command args]"
    exit 1
}

wait_for() {
    for i in `seq $TIMEOUT` ; do
        nc -z "$HOST" "$PORT" > /dev/null 2>&1 && return 0
        log INFO "Waiting for MinIO service at $HOST:$PORT..."
        sleep 1
    done
    return 1
}

while [[ $# -gt 0 ]]
do
    case "$1" in
        *:* )
        HOSTPORT=(${1//:/ })
        HOST=${HOSTPORT[0]}
        PORT=${HOSTPORT[1]}
        shift 1
        ;;
        -t)
        TIMEOUT="$2"
        if [[ "$TIMEOUT" == "" ]]; then break; fi
        shift 2
        ;;
        --quiet)
        QUIET=1
        shift 1
        ;;
        --)
        shift
        break
        ;;
        *)
        log ERROR "Unknown argument: $1"
        usage
        ;;
    esac
done

if [[ "$HOST" == "" || "$PORT" == "" ]]; then
    log ERROR "You need to provide a host and port to test."
    usage
fi

log INFO "Waiting for MinIO service at $HOST:$PORT..."

set +e
wait_for
RESULT=$?
set -e

log DEBUG "wait_for exited with status $RESULT"

if [[ $RESULT -ne 0 ]]; then
    log ERROR "Timeout occurred after waiting $TIMEOUT seconds for $HOST:$PORT"
    exit 1
fi

log INFO "MinIO service at $HOST:$PORT is available"
