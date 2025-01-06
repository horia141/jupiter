#!/bin/bash

set -ex

cd src/desktop
npx vite build
npx electron-forge start
