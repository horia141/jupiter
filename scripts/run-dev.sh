#!/bin/bash

set -ex

npx mprocs --config scripts/mprocs.dev.yaml

# npx mprocs \
#   "(cd src/webui && PORT=10020 npm run dev)" \
#  "(cd src/webapi && SQLITE_DB_URL=sqlite+aiosqlite:///../../.build-cache/juiter-fixed.sqlite  python -m watchfiles jupiter.webapi.jupiter.sync_main . ../core)"
