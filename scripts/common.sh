#!/bin/bash

export RUN_ROOT=.build-cache/run
export STANDARD_NAMESPACE=dev
export STANDARD_WEBAPI_PORT=8004
export STANDARD_WEBUI_PORT=10020

set +x
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
set -x
run_jupiter() {
    local NAMESPACE=$1
    local WEBAPI_PORT=$2
    local WEBUI_PORT=$3
    local should_wait=$4
    local should_monit=$5
    local in_ci=$6
    local mode=$7

    export local SCRIPT_ARGS=
    local platform=$(uname -s | awk '{print tolower($0)}')
    if [[ "${platform}" == "darwin" ]]
    then
        SCRIPT_ARGS="-qF"
    else
        SCRIPT_ARGS="-c"
    fi

    mkdir -p "$RUN_ROOT/$NAMESPACE"

    if [[ "$mode" == "pm2" ]]; then
        _run_jupiter_with_pm2 "$NAMESPACE" "$WEBAPI_PORT" "$WEBUI_PORT" "$should_wait" "$should_monit" "$in_ci"
    else
        _run_jupiter_with_docker "$NAMESPACE" "$WEBAPI_PORT" "$WEBUI_PORT" "$should_wait" "$should_monit" "$in_ci"
    fi
}

_run_jupiter_with_pm2() {
    export local NAMESPACE=$1
    export local WEBAPI_LOG_FILE=../../$RUN_ROOT/$NAMESPACE/webapi.log
    export local WEBAPI_SQLITE_DB_URL=sqlite+aiosqlite:///../../$RUN_ROOT/$NAMESPACE/jupiter.sqlite
    export local WEBAPI_SERVER_URL=http://0.0.0.0:${WEBAPI_PORT}
    export local WEBAPI_PORT=$2
    export local WEBUI_LOG_FILE=../../$RUN_ROOT/$NAMESPACE/webui.log
    export local WEBUI_PORT=$3
    export local WEBUI_SERVER_URL=http://0.0.0.0:${WEBUI_PORT}
    local should_wait=$4
    local should_monit=$5
    local in_ci=$6

    if [[ "$in_ci" == "dev" ]]; then
        _envsubst < scripts/pm2.config.dev.template.js > "$RUN_ROOT/$NAMESPACE/pm2.config.js"
    else
        _envsubst < scripts/pm2.config.ci.template.js > "$RUN_ROOT/$NAMESPACE/pm2.config.js"
    fi

    trap "npx pm2 delete $RUN_ROOT/$NAMESPACE/pm2.config.js" EXIT
    npx pm2 --no-color start "$RUN_ROOT/$NAMESPACE/pm2.config.js"

    echo "$WEBAPI_PORT" > "$RUN_ROOT/$NAMESPACE/webapi.port"
    echo "$WEBUI_PORT" > "$RUN_ROOT/$NAMESPACE/webui.port"

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

_run_jupiter_with_docker() {
    export local NAMESPACE=$1
    export local WEBAPI_PORT=$2
    export local WEBUI_PORT=$3
    export local WEBAPI_SERVER_URL=http://0.0.0.0:${WEBAPI_PORT}
    export local WEBUI_SERVER_URL=https://0.0.0.0:${WEBUI_PORT}
    local should_wait=$4
    local should_monit=$5
    local in_ci=$6
    export local NAME="My Hosting"
    export local AUTH_TOKEN_SECRET=$(openssl rand -hex 32)
    export local SESSION_COOKIE_SECRET=$(openssl rand -hex 32)

    export local FULLCHAIN_PEM=$(pwd)/$RUN_ROOT/$NAMESPACE/fullchain.pem
    export local PRIVKEY_PEM=$(pwd)/$RUN_ROOT/$NAMESPACE/privkey.pem

    openssl req -x509 \
        -nodes \
        -days 365 \
        -subj "/CN=localhost" \
        -newkey rsa:2048 \
        -keyout $PRIVKEY_PEM \
        -out $FULLCHAIN_PEM

    trap "docker compose -f infra/self-hosted/compose.yaml down" EXIT

    echo "$WEBAPI_PORT" > "$RUN_ROOT/$NAMESPACE/webapi.port"
    echo "$WEBUI_PORT" > "$RUN_ROOT/$NAMESPACE/webui.port"

    docker compose -f infra/self-hosted/compose.yaml up -d

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
        docker compose -f infra/self-hosted/compose.yaml logs -f
    fi
}

_envsubst() {
  python -c 'import os,sys;[sys.stdout.write(os.path.expandvars(l)) for l in sys.stdin]'
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
        port=$(jot -r 1 49152 65535)
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
        response=$(http --verify=no --timeout 10 --check-status get "${url}" 2>/dev/null)
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