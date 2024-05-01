#/bin/bash

set -ex

source scripts/common.sh

NAMESPACE=$1

if [[ -z "$NAMESPACE" ]]; then
    NAMESPACE=$STANDARD_NAMESPACE
fi
WEBAPI_PORT=$(get_jupiter_port $NAMESPACE webapi)
WEBUI_PORT=$(get_jupiter_port $NAMESPACE webui)
WEBUI_URL="http://0.0.0.0:${WEBUI_PORT}"

wait_for_service_to_start webui "$WEBUI_URL"

playwright codegen "$WEBUI_URL"
