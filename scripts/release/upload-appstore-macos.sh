#!/bin/bash

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

source secrets/Config.secrets

xcrun altool --validate-app -f .build-cache/desktop/make/Thrive-${RELEASE_VERSION}-universal.pkg --username $APPLE_ID --password $APPLE_NOTARIZATION_PASSWORD --type osx
xcrun altool --upload-app -f .build-cache/desktop/make/Thrive-${RELEASE_VERSION}-universal.pkg --type osx --username $APPLE_ID --password $APPLE_NOTARIZATION_PASSWORD
