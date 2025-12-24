#!/bin/bash

# Analytics Service - Start Script
# Port: 8009

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PID_FILE="$PROJECT_DIR/analytics_service.pid"
LOG_FILE="$PROJECT_DIR/logs/analytics_service.log"

cd "$PROJECT_DIR"

# Check if service is already running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "Analytics Service is already running (PID: $PID)"
        exit 1
    else
        echo "Removing stale PID file"
        rm -f "$PID_FILE"
    fi
fi

# Create logs directory if it doesn't exist
mkdir -p "$PROJECT_DIR/logs"

# Load environment variables
if [ -f "$PROJECT_DIR/.env" ]; then
    export $(cat "$PROJECT_DIR/.env" | grep -v '^#' | xargs)
fi

# Start the service
echo "Starting Analytics Service on port 8009..."
nohup uvicorn app.main:app --host 0.0.0.0 --port 8009 --reload >> "$LOG_FILE" 2>&1 &
PID=$!

# Save PID
echo $PID > "$PID_FILE"

echo "Analytics Service started successfully (PID: $PID)"
echo "Logs: $LOG_FILE"
echo "Service URL: http://localhost:8009"
echo "API Docs: http://localhost:8009/docs"
