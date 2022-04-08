#!/bin/bash

set -ex

cloc \
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

REQS_FILE=$(mktemp)

poetry export -f requirements.txt --output "${REQS_FILE}" --without-hashes
sed -i -e 's/; .*//g' "${REQS_FILE}"
libyear -r "${REQS_FILE}"

DEV_REQS_FILE=$(mktemp)
JUSTDEV_REQS_FILE=$(mktemp)

poetry export -f requirements.txt --output "${DEV_REQS_FILE}" --without-hashes --dev
sed -i -e 's/; .*//g' "${DEV_REQS_FILE}"
grep -Fvxf "${REQS_FILE}" "${DEV_REQS_FILE}"  > "${JUSTDEV_REQS_FILE}"
libyear -r "${JUSTDEV_REQS_FILE}"
