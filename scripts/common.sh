#!/bin/bash

get_free_port() {
    while
        port=$(shuf -n 1 -i 49152-65535)
        netstat -atun | grep -q "$port"
    do
        continue
    done

    echo "$port"
}

wait_for_service_to_start() {
    service=$1
    url=$2/healthz

    attempts=0
    max_attempts=21

    while [ $attempts -lt $max_attempts ]; do
        set +e
        response=$(http --timeout 20 --check-status get "${url}")
        resp=$?
        set -e
        
        if [ $resp -eq 0 ]; then
            echo "${service} is up and responding."
            break
        else
            echo "Waiting for ${service}. Attempt $((attempts+1)) of $max_attempts."
        fi
        
        ((attempts++))
        sleep 1  # Adjust the sleep time as needed
    done

    if [ $attempts -eq $max_attempts ]; then
        echo "Reached maximum attempts for ${service}."
        return 1
    fi
}