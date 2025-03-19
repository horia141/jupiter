#!/bin/bash

set -ex

# If the secrets/Config.secrets file does not exist, bail
if [ ! -f secrets/Config.secrets ]; then
    echo "secrets/Config.secrets file does not exist"
    exit 1
fi

source src/Config.global
source secrets/Config.secrets

AAB_OUTPUT_PATH="app/build/outputs/bundle/release"

export VERSION
export BUNDLE_ID
export PUBLIC_NAME

mkdir -p .build-cache/mobile

cd src/mobile

npx @capacitor/assets generate --iconBackgroundColor '#eeeeee' --iconBackgroundColorDark '#222222' --splashBackgroundColor '#eeeeee' --splashBackgroundColorDark '#111111'  --ios --android
npx trapeze run config.yaml --diff
ENV=production HOSTING=hosted-global BUILD_TARGET=android npx vite build --mode production --config vite.config.ts
ENV=production HOSTING=hosted-global BUILD_TARGET=android npx cap copy

cd android

./gradlew clean
./gradlew assembleRelease
./gradlew bundleRelease

jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA-256 \
  -keystore ../../../$ANDROID_UPLOAD_KEYSTORE_PATH \
  -storepass $ANDROID_UPLOAD_KEYSTORE_PASSWORD \
  -keypass $ANDROID_UPLOAD_KEYSTORE_PASSWORD \
  $AAB_OUTPUT_PATH/app-release.aab \
  $ANDROID_UPLOAD_KEYSTORE_ALIAS

mkdir -p ../../../.build-cache/mobile/android/v$VERSION
cp $AAB_OUTPUT_PATH/app-release.aab ../../../.build-cache/mobile/android/v$VERSION/app-${VERSION}.aab
