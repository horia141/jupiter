#!/bin/sh

set -ex

mkdir -p .build-cache/docs

ls -lah src
source src/Config.global

export PUBLIC_NAME
export AUTHOR
export COPYRIGHT

(cd src/docs && poetry install --only main --no-interaction --no-ansi --no-root)

mkdocs build --config-file src/docs/mkdocs.yml --site-dir ../../.build-cache/docs --clean
