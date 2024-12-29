#!/bin/bash

set -ex

source src/Config.global
source secrets/Config.secrets

cd src/mobile

npx @capacitor/assets generate --iconBackgroundColor '#eeeeee' --iconBackgroundColorDark '#222222' --splashBackgroundColor '#eeeeee' --splashBackgroundColorDark '#111111'
npx trapeze run config.yaml --diff
