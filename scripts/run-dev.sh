#!/bin/bash

set -ex

trap "npx pm2 delete all" EXIT
npx pm2 --no-color start scripts/pm2.dev.config.js
npx pm2 monit
