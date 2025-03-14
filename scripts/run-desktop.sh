#!/bin/bash

set -ex

USAGE_STRING="Usage: $0"

if [[ "${1}" == "--help" ]]
then
    echo $USAGE_STRING
    exit 0
fi

cd src/desktop
npx vite build
npx electron-forge start
