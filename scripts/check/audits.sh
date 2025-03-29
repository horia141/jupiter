#!/bin/bash

set -ex

npm audit --audit-level=info
(cd src/webui && npm audit --audit-level=high)
(cd src/desktop && npm audit --audit-level=high)
(cd src/mobile && npm audit --audit-level=high)

poetry run pip-audit -r <(poetry export -f requirements.txt --all-groups --without-hashes)
(cd src/core && poetry run pip-audit -r <(poetry export -f requirements.txt --all-groups --without-hashes))
(cd src/cli && poetry run pip-audit -r <(poetry export -f requirements.txt --all-groups --without-hashes))
(cd src/webapi && poetry run pip-audit -r <(poetry export -f requirements.txt --all-groups --without-hashes))
