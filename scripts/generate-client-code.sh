#!/bin/bash

set -ex

source scripts/common.sh

WEBAPI_PORT=$(get_free_port)
WEBAPI_URL=http://0.0.0.0:${WEBAPI_PORT}
WEBUI_PORT=$(get_free_port)

run_jupiter apigen "$WEBAPI_PORT" "$WEBUI_PORT" wait:webapi no-monit ci pm2

mkdir -p gen/ts
mkdir -p gen/py

mkdir -p .build-cache/apigen
rm -f .build-cache/apigen/openapi.json
http --timeout 2 get "$WEBAPI_URL/openapi.json" > .build-cache/apigen/openapi.json

stop_jupiter apigen

npx openapi \
    --input .build-cache/apigen/openapi.json \
    --request gen/ts/webapi-client/request-template.ts \
    --output gen/ts/webapi-client/gen \
    --client fetch \
    --name ApiClient

(cd gen/ts/webapi-client && npx tsc)

trap "rm -rf jupiter-webapi-client" EXIT
rm -rf gen/py/webapi-client
poetry run openapi-python-client generate --path .build-cache/apigen/openapi.json
mv jupiter-webapi-client gen/py/webapi-client
