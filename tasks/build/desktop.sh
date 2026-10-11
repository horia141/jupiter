#!/usr/bin/env bash

#MISE description="Build desktop app for macOS"
#USAGE flag "--log <log>" default="info" help="Log output" {
#USAGE   choices "info" "debug" "trace"
#USAGE }

set -e -o pipefail

source tasks/_common.sh

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
  rm -f src/desktop/Config.global

  # if node_modules/@jupiter/webapi-client is not a link, then we should revert it
  if [ ! -L rsc/desktop/node_modules/@jupiter/webapi-client ]; then
    rm -rf src/desktop/node_modules/@jupiter/webapi-client
    mv src/desktop/node_modules/@jupiter/webapi-client.bak src/desktop/node_modules/@jupiter/webapi-client
  fi

  # if we swapped in a copy of node_modules/@jupiter/shell, put the link back
  if [ -d src/desktop/node_modules/@jupiter/shell.bak ]; then
    rm -rf src/desktop/node_modules/@jupiter/shell
    mv src/desktop/node_modules/@jupiter/shell.bak src/desktop/node_modules/@jupiter/shell
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
    log info "secrets/Config.secrets file does not exist"
    exit 1
fi

source src/Config.global
# shellcheck disable=SC1091
source secrets/Config.secrets

sudo rm -rf .build-cache/desktop/mac-store/v${VERSION}
sudo rm -rf .build-cache/desktop/mac-web/v${VERSION}

mkdir -p .build-cache/desktop/mac-store/v${VERSION}
mkdir -p .build-cache/desktop/mac-web/v${VERSION}

trap revert_package_json EXIT
replace_package_json

log info "Building desktop app for macOS"

cp LICENSE src/desktop/LICENSE

(cd src/desktop && ENV=production npx vite build --mode production --config vite.config.ts)

# Electron forge is exceedinly stupid wrt symlinks going out of it. So
# before the build we fix this.
mv src/desktop/node_modules/@jupiter/webapi-client src/desktop/node_modules/@jupiter/webapi-client.bak
cp -r gen/ts/webapi-client src/desktop/node_modules/@jupiter/webapi-client

# The main process imports the server check from @jupiter/shell at runtime,
# and only needs its package.json and lib/.
mv src/desktop/node_modules/@jupiter/shell src/desktop/node_modules/@jupiter/shell.bak
mkdir -p src/desktop/node_modules/@jupiter/shell
cp -r src/shell/package.json src/shell/lib src/desktop/node_modules/@jupiter/shell/

mv src/desktop/assets/jupiter.icns .build-cache/jupiter.icns.bak
cp assets/jupiter.icns src/desktop/assets/jupiter.icns

mv src/desktop/assets/logo.png .build-cache/logo.png.bak
cp assets/jupiter.png src/desktop/assets/logo.png

log info "Building desktop app for macOS with forge.config.mac-store.cjs"

cp src/desktop/forge.config.mac-store.cjs src/desktop/forge.config.cjs
cp src/Config.global src/desktop/Config.global
(cd src/desktop && ENV=production DISTRIBUTION=mac-store npx electron-forge make --platform mas --arch universal)

log info "Building desktop app for macOS with forge.config.mac-web.cjs"

cp src/desktop/forge.config.mac-web.cjs src/desktop/forge.config.cjs
cp src/Config.global src/desktop/Config.global
(cd src/desktop && ENV=production DISTRIBUTION=mac-web npx electron-forge make --platform darwin --arch universal)

log info "Desktop app for macOS AppStore built in .build-cache/desktop/mac-store/v${VERSION}/make/Thrive-${VERSION}-universal.pkg"
log info "Desktop app for macOS Web built in .build-cache/desktop/mac-web/v${VERSION}/make/Thrive-${VERSION}-universal.dmg"
