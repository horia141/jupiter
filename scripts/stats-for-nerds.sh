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
  requirements.txt \
  requirements-dev.txt \
  scripts/ \
  migrations/ \
  src/

libyear -r requirements.txt
