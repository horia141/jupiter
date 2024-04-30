#!/bin/bash

set -ex

source scripts/common.sh

NAMESPACE=$1

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

run_jupiter "$NAMESPACE" "$WEBAPI_PORT" "$WEBUI_PORT" no-wait monit
