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

pyinstaller \
  --noconfirm \
  --name Thrive-Cli \
  --add-data src/cli/README.md:. \
  --add-data LICENSE:. \
  --add-data src/Config.global:. \
  --add-data src/cli/Config.project:. \
  --add-data src/core/migrations:core/migrations \
  --distpath .build-cache/standalone-binary/dist \
  --workpath .build-cache/standalone-binary/build \
  --windowed \
  --icon assets/jupiter.icns \
  src/cli/jupiter/cli/jupiter.py

if [[ "${PLATFORM}" == "darwin" ]]
then
  DMG_IMAGE_NAME="jupiter-cli-${RELEASE_VERSION}-${PLATFORM}-${ARCH}.dmg"

  rm -f rw.*.dmg
  rm -f "${DMG_IMAGE_NAME}"
  create-dmg \
    --volname "Thrive-Cli" \
    --volicon "assets/jupiter.icns" \
    --window-size 600 600 \
    --icon "Thrive-Cli.app" 40 40 \
    --hide-extension "Thrive-Cli.app" \
    --app-drop-link 200 160 \
    --eula LICENSE \
    --skip-jenkins \
    "${DMG_IMAGE_NAME}" \
    .build-cache/standalone-binary/dist/Thrive-Cli.app

  mv Thrive-Cli.spec ".build-cache/standalone-binary/Thrive-Cli.spec"
  mv "${DMG_IMAGE_NAME}" ".build-cache/standalone-binary/${DMG_IMAGE_NAME}"
fi
