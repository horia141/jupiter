#!/bin/bash

set -ex

replace_package_json() {
  # Create a backup before making changes
  cp src/desktop/package.json src/desktop/package.json.bak

  # Replace the specified strings
  sed "s|\"name\": \"@jupiter/desktop\"|\"name\": \"$PUBLIC_NAME\"|g" < src/desktop/package.json > src/desktop/package.json.1 
  sed "s|\"version\": \"0.1.0\"|\"version\": \"$VERSION\"|g" < src/desktop/package.json.1 > src/desktop/package.json
  rm src/desktop/package.json.1
}

# Function to revert changes
revert_package_json() {
  mv src/desktop/package.json.bak src/desktop/package.json
  rm -f src/desktop/package.json.1
  rm -f src/desktop/forge.config.cjs
  rm -f src/desktop/LICENSE
  rm -f src/desktop/Config.project.live

  # if node_modules/@jupiter/webapi-client is not a link, then we should revert it
  if [ ! -L rsc/desktop/node_modules/@jupiter/webapi-client ]; then
    rm -rf src/desktop/node_modules/@jupiter/webapi-client
    mv src/desktop/node_modules/@jupiter/webapi-client.bak src/desktop/node_modules/@jupiter/webapi-client
  fi

  # if src/assets/jupiter.icns is not a link, then we should revert it
  if [ ! -L src/desktop/assets/jupiter.icns ]; then
    rm -f src/desktop/assets/jupiter.icns
    mv .build-cache/jupiter.icns.bak src/desktop/assets/jupiter.icns
  fi

  # if src/assets/logo.png is not a link, then we should revert it
  if [ ! -L src/desktop/assets/logo.png ]; then
    rm -f src/desktop/assets/logo.png
    mv .build-cache/logo.png.bak src/desktop/assets/logo.png
  fi
}

# If the secrets/Config.secrets file does not exist, bail
if [ ! -f secrets/Config.secrets ]; then
    echo "secrets/Config.secrets file does not exist"
    exit 1
fi

source src/Config.global
source secrets/Config.secrets

mkdir -p .build-cache/desktop

trap revert_package_json EXIT
replace_package_json

cp LICENSE src/desktop/LICENSE

(cd src/desktop && ENV=production HOSTING=hosted-global npx vite build --mode production --config vite.config.ts)

# Electron forge is exceedinly stupid wrt symlinks going out of it. So
# before the build we fix this.
mv src/desktop/node_modules/@jupiter/webapi-client src/desktop/node_modules/@jupiter/webapi-client.bak
cp -r gen/ts/webapi-client src/desktop/node_modules/@jupiter/webapi-client

mv src/desktop/assets/jupiter.icns .build-cache/jupiter.icns.bak
cp assets/jupiter.icns src/desktop/assets/jupiter.icns

mv src/desktop/assets/logo.png .build-cache/logo.png.bak
cp assets/jupiter.png src/desktop/assets/logo.png

cp src/desktop/forge.config.mac-store.cjs src/desktop/forge.config.cjs
cp src/desktop/Config.project.live.mac-store  src/desktop/Config.project.live
(cd src/desktop && npx electron-forge make --platform mas --arch universal)
cp src/desktop/forge.config.mac-web.cjs src/desktop/forge.config.cjs
cp src/desktop/Config.project.live.mac-web  src/desktop/Config.project.live
(cd src/desktop && npx electron-forge make --platform darwin --arch universal)
