#!/bin/bash
# Stop the MCP Server (Python process)
# This does NOT stop A12 services - use stop_a12_services.sh for that

echo "Stopping MCP Server..."
echo ""

# Find and kill the server process
PID=$(ps aux | grep -i "python.*server.py" | grep -v grep | awk '{print $2}')

if [ -z "$PID" ]; then
    echo "✓ No MCP server found running"
    exit 0
fi

echo "Found MCP server process: $PID"
echo "Killing process..."
kill -9 $PID

sleep 1

# Verify it's stopped
if ps -p $PID > /dev/null 2>&1; then
    echo "❌ Failed to stop MCP server"
    exit 1
else
    echo "✓ MCP server stopped successfully"
fi
