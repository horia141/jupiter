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
  .dockerignore \
  .github/ \
  .gitignore \
  .readthedocs.yml \
  Config \
  Dockerfile \
  LICENSE \
  Makefile \
  README.md \
  docs/ \
  mkdocs.yml \
  pyproject.toml \
  scripts/ \
  migrations/ \
  jupiter/ \
  tests/ \

cat "${CLOC_BUILDINFO}"

LIBYEAR_BUILDINFO="${BUILDINFO_ROOT}/libyear"

REQS_FILE=$(mktemp)

poetry export -f requirements.txt --output "${REQS_FILE}" --without-hashes
sed -i -e 's/; .*//g' "${REQS_FILE}"
poetry run libyear -r "${REQS_FILE}" > "${LIBYEAR_BUILDINFO}"

cat "${LIBYEAR_BUILDINFO}"

DEV_LIBYEAR_BUILDINFO="${BUILDINFO_ROOT}/libyear-dev"

DEV_REQS_FILE=$(mktemp)
JUSTDEV_REQS_FILE=$(mktemp)

poetry export -f requirements.txt --output "${DEV_REQS_FILE}" --without-hashes --dev
sed -i -e 's/; .*//g' "${DEV_REQS_FILE}"
grep -Fvxf "${REQS_FILE}" "${DEV_REQS_FILE}"  > "${JUSTDEV_REQS_FILE}"
poetry run libyear -r "${JUSTDEV_REQS_FILE}" > "${DEV_LIBYEAR_BUILDINFO}"

cat "${DEV_LIBYEAR_BUILDINFO}"
