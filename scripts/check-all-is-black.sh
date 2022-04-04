#!/bin/bash

set -e

DIFF_OUTPUT=$(black --diff jupiter)

if [ -n "${DIFF_OUTPUT}" ]
then
  echo "Styling inconsistency! Please run 'make fix-style' to auto-address style issues!"
  exit 1
fi
