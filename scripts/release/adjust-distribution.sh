#!/bin/bash

set -ex

USAGE_STRING="Usage: $0 {version} --mac-store {ready|in-review|not-available} --app-store {ready|in-review|not-available} --mac-web {ready|in-review|not-available} --google-play-store {ready|in-review|not-available}"

MAC_WEB_STATUS=do-nothing
MAC_STORE_STATUS=do-nothing
APP_STORE_STATUS=do-nothing
GOOGLE_PLAY_STORE_STATUS=do-nothing

RELEASE_VERSION=$1
shift

# if release version is help
if [[ "${RELEASE_VERSION}" == "--help" ]]
then
    echo $USAGE_STRING
    exit 0
fi

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --mac-web)
            MAC_WEB_STATUS=$2
            shift 2
            ;;
        --mac-store)
            MAC_STORE_STATUS=$2
            shift 2
            ;;
        --app-store)
            APP_STORE_STATUS=$2
            shift 2
            ;;
        --google-play-store)
            GOOGLE_PLAY_STORE_STATUS=$2
            shift 2
            ;;
        --help)
            echo $USAGE_STRING
            exit 0
            ;;
        *)
            echo "Unknown parameter passed: $1"
            echo $USAGE_STRING
            exit 1
            ;;
    esac
done

if ! [[ "${RELEASE_VERSION}" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]
then
    echo "Not a valid X.Y.Z version string"
    exit 1
fi

RELEASE_TAG="v${RELEASE_VERSION}"

if ! [[ $(git tag | grep "${RELEASE_TAG}") ]]
then
    echo "Release tag ${RELEASE_VERSION} seems to not exist"
    exit 1
fi

# if MAC_WEB status is not one of do-nothing ready in-review not-available, bail
if ! [[ "${MAC_WEB_STATUS}" =~ ^(do-nothing|ready|in-review|not-available)$ ]]
then
    echo "Invalid MAC_WEB_STATUS. Should be one of do-nothing, ready, in-review, not-available"
    exit 1
fi

# if MAC_STORE status is not one of do-nothing ready in-review not-available, bail
if ! [[ "${MAC_STORE_STATUS}" =~ ^(do-nothing|ready|in-review|not-available)$ ]]
then
    echo "Invalid MAC_STORE_STATUS. Should be one of do-nothing, ready, in-review, not-available"
    exit 1
fi

# if APP_STORE status is not one of do-nothing ready in-review not-available, bail
if ! [[ "${APP_STORE_STATUS}" =~ ^(do-nothing|ready|in-review|not-available)$ ]]
then
    echo "Invalid APP_STORE_STATUS. Should be one of do-nothing, ready, in-review, not-available"
    exit 1
fi

# if GOOGLE_PLAY_STORE status is not one of do-nothing ready in-review not-available, bail
if ! [[ "${GOOGLE_PLAY_STORE_STATUS}" =~ ^(do-nothing|ready|in-review|not-available)$ ]]
then
    echo "Invalid GOOGLE_PLAY_STORE_STATUS. Should be one of do-nothing, ready, in-review, not-available"
    exit 1
fi

mkdir -p .build-cache/release/${RELEASE_VERSION}

CURRENT_MANIFEST_URL=$(gh release view ${RELEASE_TAG} --json assets | jq -r '.assets[] | select(.name == "release-manifest.json") | .url')

if [ -z "$CURRENT_MANIFEST_URL" ]
then
    cp scripts/release/release-manifest.template.json .build-cache/release/${RELEASE_VERSION}/current-release-manifest.json
else
    curl -L $CURRENT_MANIFEST_URL > .build-cache/release/${RELEASE_VERSION}/current-release-manifest.json
fi

jq --arg mac_web_status "$MAC_WEB_STATUS" \
    --arg mac_store_status "$MAC_STORE_STATUS" \
    --arg app_store_status "$APP_STORE_STATUS" \
    --arg google_play_store_status "$GOOGLE_PLAY_STORE_STATUS" \
    'if $mac_web_status != "do-nothing" then .["mac-web"] = $mac_web_status else . end |
     if $mac_store_status != "do-nothing" then .["mac-store"] = $mac_store_status else . end |
     if $app_store_status != "do-nothing" then .["app-store"] = $app_store_status else . end |
     if $google_play_store_status != "do-nothing" then .["google-play-store"] = $google_play_store_status else . end' \
    .build-cache/release/${RELEASE_VERSION}/current-release-manifest.json > .build-cache/release/${RELEASE_VERSION}/release-manifest.json

gh release upload ${RELEASE_TAG} --clobber .build-cache/release/${RELEASE_VERSION}/release-manifest.json
