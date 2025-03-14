#!/bin/bash

set -ex

USAGE_STRING="Usage: $0 {--namespace=namespace|+gen} --mode={pm2|docker}"

if [[ "${1}" == "--help" ]]
then
    echo $USAGE_STRING
    exit 0
fi

source scripts/common.sh

# Parse command line arguments
NAMESPACE=""
MODE=pm2

# Parse arguments
for arg in "$@"; do
    case $arg in
        --namespace=*)
            NAMESPACE="${arg#*=}"
            if [[ "$NAMESPACE" == "+gen" ]]; then
                NAMESPACE="+gen"
            elif [[ "$NAMESPACE" == "+"* ]]; then
                echo "Error: Invalid --namespace value. Must be a file-ish name or '+gen'."
                exit 1
            elif [[ "$NAMESPACE" != [a-zA-Z0-9_-]* ]]; then
                echo "Error: Invalid --namespace value. Must be a file-ish name or '+gen'."
                exit 1
            fi
            ;;
        --mode=*)
            MODE="${arg#*=}"
            if [[ "$MODE" != "pm2" && "$MODE" != "docker" ]]; then
                echo "Error: Invalid --mode value. Must be 'pm2' or 'docker'."
                exit 1
            fi
            ;;
        --help)
            echo $USAGE_STRING
            exit 0
            ;;
        *)
            echo "Error: Unknown argument: $arg"
            echo $USAGE_STRING
            exit 1
            ;;
    esac
done

# Set ports based on namespace
if [[ -z "${NAMESPACE}" ]]; then
    NAMESPACE=$STANDARD_NAMESPACE
    WEBAPI_PORT=$STANDARD_WEBAPI_PORT
    WEBUI_PORT=$STANDARD_WEBUI_PORT
elif [[ "${NAMESPACE}" == "--gen" ]]; then
    NAMESPACE=$(get_namespace)
    WEBAPI_PORT=$(get_free_port)
    WEBUI_PORT=$(get_free_port)
else
    WEBAPI_PORT=$(get_free_port)
    WEBUI_PORT=$(get_free_port)
fi

echo "Running Jupiter with namespace: $NAMESPACE, webapi port: $WEBAPI_PORT, webui port: $WEBUI_PORT, mode: $MODE"

run_jupiter "$NAMESPACE" "$WEBAPI_PORT" "$WEBUI_PORT" no-wait monit dev "$MODE"
