#!/bin/sh

set -ex

mkdir -p .build-cache/docs

mkdocs build --config-file mkdocs.yml --site-dir .build-cache/docs --clean
