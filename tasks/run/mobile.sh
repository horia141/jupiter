#!/usr/bin/env bash

#MISE description="Run mobile app on iOS or Android with optional instance"
#USAGE flag "--universe <universe>" default="dev" help="Jupiter universe"
#USAGE flag "--environment <environment>" default="local" help="Jupiter environment" {
#USAGE   choices "production" "staging" "local"
#USAGE }
#USAGE flag "--instance <instance>" help="Jupiter instance"
#USAGE complete "instance" run="./tasks/run/instance/_list-fast.sh"
#USAGE flag "--platform <platform>" required help="Mobile platform (ios or android)" {
#USAGE   choices "ios" "android"
#USAGE }
#USAGE flag "--log <log>" default="info" help="Log output" {
#USAGE   choices "info" "debug" "trace"
#USAGE }

: "${usage_universe:=}"
: "${usage_environment:=}"
: "${usage_platform:=}"
: "${usage_instance:=}"

set -e -o pipefail

source tasks/_common.sh

# CocoaPods (run by cap sync for iOS) fails without a UTF-8 locale.
export LANG="${LANG:-en_US.UTF-8}"
export LC_ALL="${LC_ALL:-en_US.UTF-8}"

webui_url=$(get_webui_url_for_universe "$usage_universe" "$usage_environment" "$usage_instance")
export HOSTED_GLOBAL_WEBUI_URL="$webui_url"
export BUILD_TARGET="$usage_platform"

log info "Running mobile app on $usage_platform with universe $usage_universe, environment $usage_environment, instance $usage_instance"

cd src/mobile
npx vite build
npx cap sync "$usage_platform"
npx cap run "$usage_platform"
