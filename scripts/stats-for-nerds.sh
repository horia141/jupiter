#!/bin/bash

set -ex

CURRENT_BRANCH=$(git branch --show-current)

if [[ "$CURRENT_BRANCH" =~ "release/" ]]
then
  BUILDINFO_ROOT="buildinfo/${CURRENT_BRANCH}"
else
  BUILDINFO_ROOT="buildinfo/current"
fi
CLOC_BUILDINFO="${BUILDINFO_ROOT}/cloc"

mkdir -p "${BUILDINFO_ROOT}"

cloc \
  --report-file="${CLOC_BUILDINFO}" \
  --exclude-dir="node_modules,.build-cache,build,public,.mypy_cache" \
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

cat "${CLOC_BUILDINFO}"
