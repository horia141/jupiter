#!/bin/bash

set -ex

source scripts/common.sh

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

    local namespace=$(get_namespace)
    local webapi_port=$(get_free_port)
    local webapi_url=http://0.0.0.0:${webapi_port}
    local webui_port=$(get_free_port)
    local webui_url=http://0.0.0.0:${webui_port}

    run_jupiter "$namespace" "$webapi_port" "$webui_port" wait:all no-monit

    sleep 3
    npx pm2 list

    echo "Using Web API $webapi_url and Web UI $webui_url"

    run_tests "$webapi_url" "$webui_url" "${extra_args[@]}"
}

# Function to handle the "dev" mode
dev_mode() {
    # Add your dev mode logic here
    # Check if --webui-url option is provided
    local webapi_url=
    local webui_url=
    local extra_args=()

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --webui-url)
                webui_url="$2"
                shift
                shift
                ;;
            --webapi-url)
                webapi_url="$2"
                shift
                shift
                ;;
            --namespace)
                local namespace="$2"
                local webapi_port=$(get_jupiter_port $namespace webapi)
                local webui_port=$(get_jupiter_port $namespace webui)
                webapi_url="http://0.0.0.0:$webapi_port"
                webui_url="http://0.0.0.0:$webui_port"
                shift
                shift
                ;;
            *)
                extra_args+=("$1")
                shift
                ;;
        esac
    done

    if [[ -z "$webapi_url" ]]; then
        webapi_url="http://0.0.0.0:$STANDARD_WEBAPI_PORT"
    fi

    if [[ -z $webui_url ]]; then
        webui_url="http://0.0.0.0:$STANDARD_WEBUI_PORT"
    fi

    echo "Using Web API $webapi_url and Web UI $webui_url"

    wait_for_service_to_start webapi "$webapi_url"
    wait_for_service_to_start webui "$webui_url"

    run_tests "$webapi_url" "$webui_url" --headed "${extra_args[@]}"
}

run_tests() {
    local webapi_url=$1
    shift
    local webui_url=$1
    shift

    LOCAL_WEBAPI_SERVER_URL=$webapi_url pytest itests \
        -o log_cli=true \
        --html-report=.build-cache/itest/test-report.html \
        --title="Jupiter Integration Tests" \
        --base-url="$webui_url" \
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
        echo "Usage: $0 {ci|dev [--webapi-url <URL>] [--webui-url <URL>] [--namespace <namespace>]} ...pytest-args"
        exit 1
    fi
}

# Call the main function with command line arguments
mkdir -p .build-cache/itest
main "$@"
