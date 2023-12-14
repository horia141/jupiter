#!/bin/bash

set -ex

HOST=0.0.0.0
PORT=8004
export SQLITE_DB_URL=sqlite+aiosqlite:///../../.build-cache/apigen/jupiter-gen.sqlite

mkdir -p .build-cache/apigen

cd src/webapi
uvicorn jupiter.webapi.jupiter:app --host $HOST --port $PORT &
WEBAPI_PID=$!
cd ../..

sleep 5

rm -f .build-cache/apigen/openapi.json
http --timeout 2 get localhost:${PORT}/openapi.json > .build-cache/apigen/openapi.json

kill $WEBAPI_PID

python scripts/process-openapi.py .build-cache/apigen/openapi.json

npx openapi \
    --input .build-cache/apigen/openapi.json \
    --request gen/request-template.ts \
    --output gen/gen \
    --client fetch \
    --name ApiClient

(cd gen && npx tsc)
