#!/bin/bash

set -ex

source src/Config.global
source secrets/Config.secrets

mkdir -p .build-cache/cloc

CLOC_FILE=.build-cache/cloc/$VERSION

cloc \
  --report-file="${CLOC_FILE}" \
  --exclude-dir="node_modules,.build-cache,build,public,.mypy_cache,ios,android" \
  --not-match-f="(package-lock.json|poetry.lock)" \
  .dockerignore \
  .eslintignore \
  .prettierignore \
  .gitignore \
  .github/ \
  LICENSE \
  Makefile \
  README.md \
  docs/ \
  scripts/ \
  src/ \
  itests/ \

cat "${CLOC_FILE}"
