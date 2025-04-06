#!/bin/bash

set -ex

source scripts/common.sh

USAGE_STRING="Usage: $0 {--namespace=namespace}"

if [[ "${1}" == "--help" ]]
then
    echo $USAGE_STRING
    exit 0
fi

NAMESPACE="$STANDARD_NAMESPACE"

# Parse arguments
for arg in "$@"; do
    case $arg in
        --namespace=*)
            NAMESPACE="${arg#*=}"
        ;;
        *)
            echo "Error: Invalid argument: $arg"
            echo $USAGE_STRING
            exit 1
        ;;
    esac
done

WEBUI_PORT=$(get_jupiter_port "$NAMESPACE" "webui")
export HOSTED_GLOBAL_WEBUI_URL="http://localhost:$WEBUI_PORT"

cd src/desktop
npx vite build
npx electron-forge start
