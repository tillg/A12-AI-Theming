#!/bin/bash
# Stop A12 application services (backend + frontend)
# This does NOT stop the MCP server - use stop_mcp_server.sh for that

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Stopping A12 Application Services..."
echo ""

# Stop frontend (npm)
echo "1. Stopping frontend (npm)..."
pkill -f "npm start" && echo "   ✓ Frontend stopped" || echo "   No npm process found"

# Stop backend (gradle/docker)
echo "2. Stopping backend (Docker + Gradle)..."
cd "$PROJECT_ROOT"
gradle composeDown && echo "   ✓ Backend stopped" || echo "   Docker may already be down"

echo ""
echo "Done! Verify with: python check_a12_services.py"
