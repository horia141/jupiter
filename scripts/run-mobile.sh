#!/bin/bash

set -ex

USAGE_STRING="Usage: $0 {ios|android}"

# Run the mobile app. ./scripts/run-mobile.sh {ios|android}
PLATFORM=$1

if [[ "${PLATFORM}" == "--help" ]]
then
    echo $USAGE_STRING
    exit 0
fi

if [[ "${PLATFORM}" != "ios" && "${PLATFORM}" != "android" ]]
then
    echo "Unknown platform: ${PLATFORM}"
    echo $USAGE_STRING
    exit 1
fi

cd src/mobile && npx cap run $PLATFORM
