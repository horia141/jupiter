#!/bin/bash

set -ex

USAGE_STRING="Usage: $0 {version} --desktop-macos --mobile-ios --mobile-android"

# The command like looks like this
# ./upload-gh.sh {version} --desktop-macos --mobile-ios --mobile-android
# we parse it here
DESKTOP_MACOS=false
MOBILE_IOS=false
MOBILE_ANDROID=false

RELEASE_VERSION=$1
shift

if [[ "${RELEASE_VERSION}" == "--help" ]]
then
    echo $USAGE_STRING
    exit 0
fi

while [ "$#" -gt 0 ]; do
    case "$1" in
        --desktop-macos)
            DESKTOP_MACOS=true
            ;;
        --mobile-ios)
            MOBILE_IOS=true
            ;;
        --mobile-android)
            MOBILE_ANDROID=true
            ;;
        --help)
            echo $USAGE_STRING
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo $USAGE_STRING
            exit 1
            ;;
    esac
    shift
done

echo "Uploading release ${RELEASE_VERSION} to GitHub with desktop-macos=${DESKTOP_MACOS}, mobile-ios=${MOBILE_IOS}, mobile-android=${MOBILE_ANDROID}"

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

RELEASE_NOTES_PATH="src/docs/material/releases/version-${RELEASE_VERSION}.md"

# if the release notes file does not exist, bail
if [ ! -f "${RELEASE_NOTES_PATH}" ]; then
    echo "Release notes file does not exist"
    exit 1
fi

rm -rf .build-cache/release/${RELEASE_VERSION}
mkdir -p .build-cache/release/${RELEASE_VERSION}

jq --arg desktop_macos "$DESKTOP_MACOS" \
    --arg mobile_ios "$MOBILE_IOS" \
    --arg mobile_android "$MOBILE_ANDROID" \
    'if $desktop_macos == "true" then 
          .["mac-web"] = "ready" | .["mac-store"] = "in-review" 
     else 
          .["mac-web"] = "not-available" | .["mac-store"] = "not-available" 
     end |
     if $mobile_ios == "true" then 
          .["app-store"] = "in-review" 
     else 
          .["app-store"] = "not-available" 
     end |
     if $mobile_android == "true" then 
          .["google-play-store"] = "in-review" 
     else 
          .["google-play-store"] = "not-available" 
     end' scripts/release/release-manifest.template.json > .build-cache/release/${RELEASE_VERSION}/release-manifest.json

exit 1

gh release create ${RELEASE_TAG} --draft --verify-tag --title "v${RELEASE_VERSION}" --notes-file "${RELEASE_NOTES_PATH}"

gh release upload ${RELEASE_TAG} --clobber .build-cache/release/${RELEASE_VERSION}/release-manifest.json

if [ ! -f .build-cache/cloc/${RELEASE_VERSION} ]; then
    echo "Cloc file does not exist"
    exit 1
fi

gh release upload ${RELEASE_TAG} --clobber .build-cache/cloc/${RELEASE_VERSION}

if [ "${DESKTOP_MACOS}" = true ]; then
    # if the releases don't exist
    if [ ! -f .build-cache/desktop/make/Thrive-${RELEASE_VERSION}-universal.pkg ] || [ ! -f .build-cache/desktop/make/Thrive-${RELEASE_VERSION}-universal.dmg ]; then
        echo "Desktop macOS releases do not exist"
        exit 1
    fi

    gh release upload ${RELEASE_TAG} --clobber .build-cache/desktop/make/Thrive-${RELEASE_VERSION}-universal.pkg
    gh release upload ${RELEASE_TAG} --clobber .build-cache/desktop/make/Thrive-${RELEASE_VERSION}-universal.dmg
fi

if [ "${MOBILE_IOS}" = true ]; then
    if [ ! -f .build-cache/mobile/ios/v${RELEASE_VERSION}/build/App-${RELEASE_VERSION}.ipa ]; then
        echo "iOS release does not exist"
        exit 1
    fi

    gh release upload ${RELEASE_TAG} --clobber .build-cache/mobile/ios/v${RELEASE_VERSION}/build/App-${RELEASE_VERSION}.ipa
fi

if [ "${MOBILE_ANDROID}" = true ]; then
    if [ ! -f .build-cache/mobile/android/v${RELEASE_VERSION}/build/Thrive-${RELEASE_VERSION}.apk ]; then
        echo "Android release does not exist"
        exit 1
    fi

    gh release upload ${RELEASE_TAG} --clobber .build-cache/mobile/android/v${RELEASE_VERSION}/build/Thrive-${RELEASE_VERSION}.apk
fi

gh release edit ${RELEASE_TAG} --draft=false
