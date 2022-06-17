#!/bin/bash

set -ex

RELEASE_BRANCH=$(git rev-parse --abbrev-ref HEAD)

if ! [[ "${RELEASE_BRANCH}" =~ "release/" ]]
then
    RELEASE_VERSION="current"
else
    RELEASE_VERSION=${RELEASE_BRANCH/release\/}
fi

PLATFORM=$(uname -s | awk '{print tolower($0)}')
ARCH=$(arch)

poetry run pyinstaller \
  --noconfirm \
  --name Jupiter \
  --add-data README.md:. \
  --add-data LICENSE:. \
  --add-data Config:. \
  --add-data migrations:migrations \
  --distpath .build-cache/standalone-binary/dist \
  --workpath .build-cache/standalone-binary/build \
  --windowed \
  --icon assets/jupiter.icns \
  jupiter/jupiter.py

if [[ "${PLATFORM}" == "darwin" ]]
then
  DMG_IMAGE_NAME="jupiter-${RELEASE_VERSION}-${PLATFORM}-${ARCH}.dmg"

  rm -f rw.*.dmg
  rm -f "${DMG_IMAGE_NAME}"
  create-dmg \
    --volname "Jupiter" \
    --volicon "assets/jupiter.icns" \
    --window-size 600 600 \
    --icon "Jupiter.app" 40 40 \
    --hide-extension "Jupiter.app" \
    --app-drop-link 200 160 \
    --eula LICENSE \
    --skip-jenkins \
    "${DMG_IMAGE_NAME}" \
    .build-cache/standalone-binary/dist/Jupiter.app

  mv Jupiter.spec ".build-cache/standalone-binary/Jupiter.spec"
  mv "${DMG_IMAGE_NAME}" ".build-cache/standalone-binary/${DMG_IMAGE_NAME}"
fi
