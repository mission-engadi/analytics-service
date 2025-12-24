#!/bin/bash

# Analytics Service - Stop Script

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PID_FILE="$PROJECT_DIR/analytics_service.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "Analytics Service is not running (no PID file found)"
    exit 1
fi

PID=$(cat "$PID_FILE")

if ! ps -p "$PID" > /dev/null 2>&1; then
    echo "Analytics Service is not running (process not found)"
    rm -f "$PID_FILE"
    exit 1
fi

echo "Stopping Analytics Service (PID: $PID)..."
kill "$PID"

# Wait for process to stop
for i in {1..10}; do
    if ! ps -p "$PID" > /dev/null 2>&1; then
        echo "Analytics Service stopped successfully"
        rm -f "$PID_FILE"
        exit 0
    fi
    sleep 1
done

# Force kill if still running
echo "Force stopping Analytics Service..."
kill -9 "$PID"
rm -f "$PID_FILE"
echo "Analytics Service stopped (forced)"
