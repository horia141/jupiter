#!/bin/bash

set -ex

# If the secrets/Config.secrets file does not exist, bail
if [ ! -f secrets/Config.secrets ]; then
    echo "secrets/Config.secrets file does not exist"
    exit 1
fi

source src/Config.global
source secrets/Config.secrets

export VERSION
export BUNDLE_ID
export PUBLIC_NAME

WORKSPACE=ios/App/App.xcworkspace
SCHEME=App
CONFIGURATION=Release
ARCHIVE_PATH=../../.build-cache/mobile/ios/v${VERSION}/build.xcarchive
EXPORT_OPTIONS_PLIST=ios/App/archive.plist
IPA_PATH=../../.build-cache/mobile/ios/v${VERSION}/build

mkdir -p .build-cache/mobile

cd src/mobile

npx @capacitor/assets generate --iconBackgroundColor '#eeeeee' --iconBackgroundColorDark '#222222' --splashBackgroundColor '#eeeeee' --splashBackgroundColorDark '#111111'  --ios --android
npx trapeze run config.yaml --diff
ENV=production HOSTING=hosted-global BUILD_TARGET=ios npx vite build --mode production --config vite.config.ts
ENV=production HOSTING=hosted-global npx cap copy

xcodebuild clean \
    -workspace "$WORKSPACE" \
    -scheme "$SCHEME" \
    -configuration "$CONFIGURATION"

xcodebuild archive \
    -workspace "$WORKSPACE" \
    -scheme "$SCHEME" \
    -configuration "$CONFIGURATION" \
    -archivePath "$ARCHIVE_PATH" \
    -allowProvisioningUpdates


xcodebuild -exportArchive \
    -archivePath "$ARCHIVE_PATH" \
    -exportOptionsPlist "$EXPORT_OPTIONS_PLIST" \
    -exportPath "$IPA_PATH"

cp $IPA_PATH/App.ipa $IPA_PATH/App-${VERSION}.ipa
