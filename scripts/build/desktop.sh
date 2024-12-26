#!/bin/sh

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
  rm -f src/desktop/forge.config.js
  rm -f src/desktop/LICENSE
  # if node_modules/@jupiter/webapi-client is not a link, then we should revert it
  if [ ! -L node_modules/@jupiter/webapi-client ]; then
    rm -rf src/desktop/node_modules/@jupiter/webapi-client
    mv src/desktop/node_modules/@jupiter/webapi-client.bak src/desktop/node_modules/@jupiter/webapi-client
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

# Electron forge is exceedinly stupid wrt symlinks going out of it. So
# before the build we fix this.
mv src/desktop/node_modules/@jupiter/webapi-client src/desktop/node_modules/@jupiter/webapi-client.bak
cp -r gen/ts/webapi-client src/desktop/node_modules/@jupiter/webapi-client

cp src/desktop/forge.config.mas.js src/desktop/forge.config.js
(cd src/desktop && npx electron-forge make --platform mas --arch universal)
cp src/desktop/forge.config.darwin.js src/desktop/forge.config.js
(cd src/desktop && npx electron-forge make --platform darwin --arch universal)
