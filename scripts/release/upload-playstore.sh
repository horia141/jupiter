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

source src/Config.global
source secrets/Config.secrets

export GOOGLE_APPLICATION_CREDENTIALS=./secrets/play-store-bundle-uploader-key.json

ACCESS_TOKEN=$(gcloud auth application-default print-access-token --scopes=https://www.googleapis.com/auth/androidpublisher)

# Start the edit

EDIT_ID=$(curl -X POST \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    https://androidpublisher.googleapis.com/androidpublisher/v3/applications/${BUNDLE_ID}/edits | jq -r '.id')

# Upload the bundle

curl -X POST \
    -T .build-cache/mobile/android/v${RELEASE_VERSION}/app-${RELEASE_VERSION}.aab \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/octet-stream" \
    "https://androidpublisher.googleapis.com/upload/androidpublisher/v3/applications/${BUNDLE_ID}/edits/${EDIT_ID}/bundles"

# Close the edit

curl -X POST \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    https://androidpublisher.googleapis.com/androidpublisher/v3/applications/${BUNDLE_ID}/edits/${EDIT_ID}:commit
