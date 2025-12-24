#!/bin/bash

# Analytics Service - Restart Script

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "Restarting Analytics Service..."

# Stop the service
"$SCRIPT_DIR/stop.sh"

# Wait a moment
sleep 2

# Start the service
"$SCRIPT_DIR/start.sh"
