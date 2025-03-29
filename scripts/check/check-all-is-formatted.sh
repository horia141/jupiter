#!/bin/bash

set -ex

if ! poetry run autoflake --check --config=scripts/check/lint/autoflake src/core src/cli src/webapi itests
then
  echo "Styling inconsistency! Please run 'make fix-style' to auto-address style issues!"
  exit 1
fi

if ! poetry run black --check src/core src/cli src/webapi itests
then
  echo "Styling inconsistency! Please run 'make fix-style' to auto-address style issues!"
  exit 1
fi

if ! npx prettier --check src/webui src/desktop src/mobile
then
  echo "Styling inconsistency! Please run 'make fix-style' to auto-address style issues!"
  exit 1
fi
