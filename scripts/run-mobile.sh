#!/bin/bash

set -ex

source scripts/common.sh

USAGE_STRING="Usage: $0 {ios|android} {--namespace=namespace}"

PLATFORM=$1

if [[ "${PLATFORM}" == "--help" || -z "${PLATFORM}" ]]
then
    echo $USAGE_STRING
    exit 0
fi

shift

NAMESPACE="$STANDARD_NAMESPACE"

for arg in "$@"; do
    case $arg in
        --namespace=*)
            NAMESPACE="${arg#*=}"
        ;;
        *)
            echo "Unknown argument: ${arg}"
            echo $USAGE_STRING
            exit 1
        ;;
    esac
done

if [[ "${PLATFORM}" != "ios" && "${PLATFORM}" != "android" ]]
then
    echo "Unknown platform: ${PLATFORM}"
    echo $USAGE_STRING
    exit 1
fi

WEBUI_PORT=$(get_jupiter_port "$NAMESPACE" "webui")
export HOSTED_GLOBAL_WEBUI_URL="http://localhost:$WEBUI_PORT"
export BUILD_TARGET=$PLATFORM

cd src/mobile
npx vite build
npx cap run $PLATFORM
