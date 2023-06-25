#!/bin/bash

set -ex

if ! poetry run autoflake --check --config=scripts/lint/autoflake src/core src/cli src/webapi tests
then
  echo "Styling inconsistency! Please run 'make fix-style' to auto-address style issues!"
  exit 1
fi

if ! poetry run black --check src/core src/cli src/webapi tests
then
  echo "Styling inconsistency! Please run 'make fix-style' to auto-address style issues!"
  exit 1
fi

if ! npx prettier --check src/webui src/desktop
then
  echo "Styling inconsistency! Please run 'make fix-style' to auto-address style issues!"
  exit 1
fi
