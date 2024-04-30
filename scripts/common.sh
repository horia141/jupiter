#!/bin/bash

export RUN_ROOT=.build-cache/run
export STANDARD_NAMESPACE=dev
export STANDARD_WEBAPI_PORT=8004
export STANDARD_WEBUI_PORT=10020

run_jupiter() {
    export local NAMESPACE=$1
    export local WEBAPI_LOG_FILE=../../$RUN_ROOT/$NAMESPACE/webapi.log
    export local WEBAPI_SQLITE_DB_URL=sqlite+aiosqlite:///../../$RUN_ROOT/$NAMESPACE/jupiter.sqlite
    export local WEBAPI_PORT=$2
    export local WEBAPI_SERVER_URL=http://0.0.0.0:${WEBAPI_PORT}
    export local WEBUI_LOG_FILE=../../$RUN_ROOT/$NAMESPACE/webui.log
    export local WEBUI_PORT=$3
    export local WEBUI_SERVER_URL=http://0.0.0.0:${WEBUI_PORT}
    local should_wait=$4
    local should_monit=$5

    mkdir -p "$RUN_ROOT/$NAMESPACE"
    envsubst < scripts/pm2.config.template.js > "$RUN_ROOT/$NAMESPACE/pm2.config.js"

    trap "npx pm2 delete $RUN_ROOT/$NAMESPACE/pm2.config.js" EXIT
    npx pm2 --no-color start "$RUN_ROOT/$NAMESPACE/pm2.config.js"

    echo "$WEBAPI_PORT" > "$RUN_ROOT/$NAMESPACE/webapi.port"
    echo "$WEBUI_PORT" > "$RUN_ROOT/$NAMESPACE/webui.port"

    sleep 3
    npx pm2 list

    if [[ "$should_wait" == "wait:all" ]]; then
        wait_for_service_to_start webapi "$WEBAPI_SERVER_URL"
        wait_for_service_to_start webui "$WEBUI_SERVER_URL"
    fi

    if [[ ${should_wait} == "wait:webapi" ]]; then
        wait_for_service_to_start webapi "$WEBAPI_SERVER_URL"
    fi 

    if [[ ${should_wait} == "wait:webui" ]]; then
        wait_for_service_to_start webui "$WEBUI_SERVER_URL"
    fi

    if [[ ${should_monit} == "monit" ]]; then
        npx pm2 monit
    fi
}

stop_jupiter() {
    local service=$1

    npx pm2 delete "$RUN_ROOT/$service/pm2.config.js"
}

get_jupiter_port() {
    local namespace=$1
    local service=$2

    if ! [[ -f "$RUN_ROOT/$namespace/$service.port" ]]; then
        echo "Port file not found for $service in $namespace namespace."
        exit 1
    fi

    cat "$RUN_ROOT/$namespace/$service.port"
}

get_namespace() {
    poetry run randomname generate
}

get_free_port() {
    local port=
    while
        port=$(shuf -n 1 -i 49152-65535)
        netstat -atun | grep -q "$port"
    do
        continue
    done

    echo "$port"
}

wait_for_service_to_start() {
    local service=$1
    local url=${2/0.0.0.0/localhost}/healthz

    local attempts=0
    local max_attempts=21

    while [ "$attempts" -lt "$max_attempts" ]; do
        set +e
        response=$(http --timeout 10 --check-status get "${url}" 2>/dev/null)
        resp=$?
        set -e
        
        if [ "$resp" -eq 0 ]; then
            echo "${service} is up and responding."
            break
        else
            echo "Waiting for ${service}. Attempt $((attempts+1)) of $max_attempts."
        fi
        
        attempts=$(expr $attempts + 1)
        sleep 1  # Adjust the sleep time as needed
    done

    if [ "$attempts" -eq "$max_attempts" ]; then
        echo "Reached maximum attempts for ${service}."
        return 1
    fi
}