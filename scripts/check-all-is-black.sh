#!/bin/bash

set -ex

if ! poetry run black --check jupiter
then
  echo "Styling inconsistency! Please run 'make fix-style' to auto-address style issues!"
  exit 1
fi
