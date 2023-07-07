#!/bin/bash

set -ex

export PORT=10020
(cd src/webui && npm run dev) &
(cd src/webapi && SQLITE_DB_URL=sqlite+aiosqlite:///../../.build-cache/jupiter-dev.sqlite  uvicorn jupiter.webapi.jupiter:app --port 8010 --reload --reload-dir . --reload-dir ../core)
