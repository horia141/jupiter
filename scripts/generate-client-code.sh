#!/bin/bash

set -ex

source scripts/common.sh

export HOST=0.0.0.0
export PORT=8004
export SQLITE_DB_URL=sqlite+aiosqlite:///../../.build-cache/apigen/jupiter-gen.sqlite

mkdir -p .build-cache/apigen

cd src/webapi
python -m jupiter.webapi.jupiter &
WEBAPI_PID=$!
cd ../..

wait_for_service_to_start webapi http://localhost:${PORT}

rm -f .build-cache/apigen/openapi.json
http --timeout 2 get 127.0.0.1:${PORT}/openapi.json > .build-cache/apigen/openapi.json

kill $WEBAPI_PID

python scripts/process-openapi.py .build-cache/apigen/openapi.json

npx openapi \
    --input .build-cache/apigen/openapi.json \
    --request gen/ts/webapi-client/request-template.ts \
    --output gen/ts/webapi-client/gen \
    --client fetch \
    --name ApiClient

(cd gen/ts/webapi-client && npx tsc)
