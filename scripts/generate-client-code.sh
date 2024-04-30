#!/bin/bash

set -ex

source scripts/common.sh

WEBAPI_PORT=$(get_free_port)
WEBUI_PORT=$(get_free_port)

run_jupiter apigen $WEBAPI_PORT $WEBUI_PORT wait:webapi no-monit

mkdir -p gen/ts
mkdir -p gen/py

rm -f .build-cache/apigen/openapi.json
http --timeout 2 get http://0.0.0.0:${WEBAPI_PORT}/openapi.json > .build-cache/apigen/openapi.json

stop_jupiter apigen

npx openapi \
    --input .build-cache/apigen/openapi.json \
    --request gen/ts/webapi-client/request-template.ts \
    --output gen/ts/webapi-client/gen \
    --client fetch \
    --name ApiClient

(cd gen/ts/webapi-client && npx tsc)

trap "rm -rf jupiter-webapi-client" EXIT
if [[ -d gen/py/webapi-client ]]; then
    mv gen/py/webapi-client jupiter-webapi-client
    poetry run openapi-python-client update --path .build-cache/apigen/openapi.json
    mv jupiter-webapi-client gen/py/webapi-client
else
    poetry run openapi-python-client generate --path .build-cache/apigen/openapi.json
    mv jupiter-webapi-client gen/py/webapi-client
fi
