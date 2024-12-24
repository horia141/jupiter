#!/bin/sh

set -ex

mkdir -p .build-cache/docs

(cd src/docs && poetry install --only main --no-interaction --no-ansi --no-root)

source src/Config.global

export PUBLIC_NAME
export AUTHOR
export COPYRIGHT

mkdocs build --config-file src/docs/mkdocs.yml --site-dir ../../.build-cache/docs --clean
