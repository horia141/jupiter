#!/bin/bash

set -ex

RELEASE_VERSION=$1

if ! [[ "${RELEASE_VERSION}" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]
then
    echo "Not a valid X.Y.Z version string"
    exit 1
fi

RELEASE_TAG="v${RELEASE_VERSION}"
RELEASE_BRANCH="release/"v${RELEASE_VERSION}""

# shellcheck disable=SC2143
if [[ $(git tag | grep "${RELEASE_TAG}") ]]
then
    echo "Release ${RELEASE_VERSION} seems to already exist"
    exit 1
fi

if [[ $(git rev-parse --abbrev-ref HEAD) != develop ]]
then
    echo "Must be on the develop branch"
    exit 1
fi

RELEASE_NOTES_PATH="src/docs/material/releases/version-${RELEASE_VERSION}.md"
RELEASE_DATE=$(date +"%Y/%m/%d")

git pull
git checkout -b "${RELEASE_BRANCH}"
sed -E "s/VERSION=.+/VERSION=${RELEASE_VERSION}/g" < src/Config.global > src/Config.global.bak
mv src/Config.global.bak src/Config.global
cp scripts/docs/template.md "${RELEASE_NOTES_PATH}"
sed -i "" -E "s/{{release_version}}/${RELEASE_VERSION}/g" "${RELEASE_NOTES_PATH}"
sed -i "" -E "s|{{release_date}}|${RELEASE_DATE}|g" "${RELEASE_NOTES_PATH}"
git add "${RELEASE_NOTES_PATH}"
