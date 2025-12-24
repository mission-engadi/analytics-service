#!/bin/bash

# Analytics Service - Status Script

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PID_FILE="$PROJECT_DIR/analytics_service.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "Analytics Service is NOT running (no PID file)"
    exit 1
fi

PID=$(cat "$PID_FILE")

if ps -p "$PID" > /dev/null 2>&1; then
    echo "Analytics Service is RUNNING (PID: $PID)"
    echo "Port: 8009"
    echo "Service URL: http://localhost:8009"
    echo "API Docs: http://localhost:8009/docs"
    echo ""
    echo "Process info:"
    ps -p "$PID" -o pid,ppid,cmd,%mem,%cpu,etime
    exit 0
else
    echo "Analytics Service is NOT running (process not found)"
    rm -f "$PID_FILE"
    exit 1
fi
