#!/bin/sh

set -ex

RELEASE_VERSION=$1

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

gh release create ${RELEASE_TAG} --draft --verify-tag --title "v${RELEASE_VERSION}" --notes-file "${RELEASE_NOTES_PATH}"

gh release upload ${RELEASE_TAG} --clobber .build-cache/desktop/make/Thrive-${RELEASE_VERSION}-universal.pkg
gh release upload ${RELEASE_TAG} --clobber .build-cache/desktop/make/Thrive-${RELEASE_VERSION}-universal.dmg
gh release upload ${RELEASE_TAG} --clobber .build-cache/mobile/ios/v${RELEASE_VERSION}/build/App.ipa

gh release edit ${RELEASE_TAG} --draft=false
