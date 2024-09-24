#!/usr/bin/env bash
set -e

TIMEOUT=15
QUIET=0
HOST=""
PORT=""

echoerr() { if [ "$QUIET" -ne 1 ]; then echo "$@" 1>&2; fi }

usage() {
    echo "Usage: $0 host:port [-t timeout] [-- command args]"
    exit 1
}

wait_for() {
    for i in `seq $TIMEOUT` ; do
        nc -z "$HOST" "$PORT" > /dev/null 2>&1 && return 0
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
        echoerr "Unknown argument: $1"
        usage
        ;;
    esac
done

if [[ "$HOST" == "" || "$PORT" == "" ]]; then
    echoerr "Error: you need to provide a host and port to test."
    usage
fi

echoerr "Waiting for $HOST:$PORT..."

set +e
wait_for
RESULT=$?
set -e

echoerr "Debug: wait_for exited with status $RESULT"

if [[ $RESULT -ne 0 ]]; then
    echoerr "Timeout occurred after waiting $TIMEOUT seconds for $HOST:$PORT"
    exit 1
fi

echoerr "$HOST:$PORT is available"
