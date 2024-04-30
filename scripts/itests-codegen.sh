#/bin/bash

set -ex

NAMESPACE=$1
WEBAPI_PORT=$(get_service_port $NAMESPACE webapi)
WEBUI_PORT=$(get_service_port $NAMESPACE webui)
WEBUI_URL="http://0.0.0.0:${WEBUI_PORT}"

wait_for_service_to_start webui "$WEBUI_URL"

playwright codegen "$WEBUI_URL"
