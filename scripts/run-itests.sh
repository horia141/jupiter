#!/bin/bash

set -ex

source scripts/common.sh

mkdir -p .build-cache/itest

WEBAPI_PORT=$(get_free_port)
WEBUI_PORT=$(get_free_port)
export SQLITE_DB_URL=sqlite+aiosqlite:///../../.build-cache/itest/jupiter.sqlite


ci_mode() {
    # Add your ci mode logic here
    local extra_args=()

    while [[ $# -gt 0 ]]; do
        case "$1" in
            *)
                extra_args+=("$1")
                shift
                ;;
        esac
    done

    trap "npx pm2 delete webapi:${WEBAPI_PORT} webui:${WEBUI_PORT}" EXIT

    HOST=0.0.0.0 PORT=$WEBAPI_PORT npx pm2 start --name=webapi:${WEBAPI_PORT} --interpreter=none --no-autorestart --cwd=src/webapi python -- -m jupiter.webapi.jupiter
    LOCAL_WEBAPI_SERVER_URL=http://0.0.0.0:$WEBAPI_PORT HOST=0.0.0.0 PORT=$WEBUI_PORT npx pm2 start --name=webui:${WEBUI_PORT} --interpreter=none --no-autorestart --cwd=src/webui npm -- run dev
    
    echo "Using Web API $webapi_url and Web UI $webui_url"

    wait_for_service_to_start webapi http://0.0.0.0:$WEBAPI_PORT
    wait_for_service_to_start webui http://0.0.0.0:$WEBUI_PORT

    run_tests http://0.0.0.0:$WEBAPI_PORT http://0.0.0.0:$WEBUI_PORT "${extra_args[@]}"
}

# Function to handle the "dev" mode
dev_mode() {
    # Add your dev mode logic here
    # Check if --webui-url option is provided
    local webapi_url="http://0.0.0.0:8010"
    local webui_url="http://0.0.0.0:10020"
    local extra_args=()

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --webui-url)
                webui_url="$2"
                shift
                shift
                ;;
            *)
                extra_args+=("$1")
                shift
                ;;
        esac
    done

    echo "Using Web API $webapi_url and Web UI $webui_url"

    wait_for_service_to_start webapi $webapi_url
    wait_for_service_to_start webui $webui_url

    run_tests $webapi_url $webui_url --headed "${extra_args[@]}"
}

run_tests() {
    echo $@
    local webapi_url=$1
    shift
    local webui_url=$1
    shift

    LOCAL_WEBAPI_SERVER_URL=$webapi_url pytest itests \
        -o log_cli=true \
        --html-report=.build-cache/itest/test-report.html \
        --title="Jupiter Integration Tests" \
        --base-url=$webui_url \
        "$@"
}

# Main function
main() {
    if [ "$1" == "ci" ]; then
        shift
        ci_mode "$@"
    elif [ "$1" == "dev" ]; then
        shift
        dev_mode "$@"
    else
        echo "Usage: $0 {ci|dev [--webui-url <URL>]} ...pytest-args"
        exit 1
    fi
}

# Call the main function with command line arguments
main "$@"
