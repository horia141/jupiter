#!/bin/bash

set -ex

source scripts/common.sh

mkdir -p .build-cache/itest

WEBAPI_PORT=$(get_free_port)
WEBAPI_PID=
WEBUI_PORT=$(get_free_port)
WEBUI_PID=
export SQLITE_DB_URL=sqlite+aiosqlite:///../../.build-cache/itest/jupiter.sqlite

kill_jupiter() {
    if [ -n "$WEBAPI_PID" ]; then
        kill $WEBAPI_PID
    fi
    WEBAPI_PID=$(netstat -anvp tcp | grep -m 1 $WEBAPI_PORT | awk '{split($9, a, "/"); print a[1]}')
    if [ -n "$WEBAPI_PID" ]; then
        kill $WEBAPI_PID
    fi
    if [ -n "$WEBUI_PID" ]; then
        pkill -P $WEBUI_PID
    fi
    WEBUI_PID=$(netstat -anvp tcp | grep -m 1 $WEBUI_PORT | awk '{split($9, a, "/"); print a[1]}')
    if [ -n "$WEBUI_PID" ]; then
        pkill -P $WEBUI_PID
    fi
}

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

    trap kill_jupiter EXIT
    
    cd src/webapi
    HOST=0.0.0.0 PORT=$WEBAPI_PORT python -m jupiter.webapi.jupiter &
    WEBAPI_PID=$!
    cd ../..

    cd src/webui
    LOCAL_WEBAPI_SERVER_URL=http://localhost:$WEBAPI_PORT PORT=$WEBUI_PORT npm run dev &
    WEBUI_PID=$!
    cd ../..

    wait_for_service_to_start webapi http://localhost:$WEBAPI_PORT
    wait_for_service_to_start webui http://localhost:$WEBUI_PORT

    run_tests http://localhost:$WEBUI_PORT "${extra_args[@]}"

    kill $WEBAPI_PID
    kill $WEBUI_PID
}

# Function to handle the "dev" mode
dev_mode() {
    # Add your dev mode logic here
    # Check if --webui-url option is provided
    local webui_url="http://localhost:10020"
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

    echo "Using web UI URL: $webui_url"

    wait_for_service_to_start webui $webui_url

    run_tests $webui_url --headed "${extra_args[@]}"
}

run_tests() {
    local webui_url=$1
    shift

    pytest itests \
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
        echo "Usage: $0 {ci|dev [--webui-url <URL>]}"
        exit 1
    fi
}

# Call the main function with command line arguments
main "$@"
