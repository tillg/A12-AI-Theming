#!/usr/bin/env python3
"""Check the status of A12 application services (backend and frontend).

This checks if the A12 app (not the MCP server) is running.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from services.process_manager import ProcessManager


async def main():
    """Check service status."""
    print("=" * 80)
    print("A12 Theme Development Environment - Service Status Check")
    print("=" * 80)
    print()

    # Check backend
    print("Checking Backend (http://localhost:8082)...")
    backend_healthy = await ProcessManager.is_backend_healthy()
    if backend_healthy:
        print("  ✅ Backend is UP and responding")
    else:
        print("  ❌ Backend is DOWN or not responding")
    print()

    # Check frontend
    print("Checking Frontend (http://localhost:8081)...")
    frontend_healthy = await ProcessManager.is_frontend_healthy()
    if frontend_healthy:
        print("  ✅ Frontend is UP and responding")
    else:
        print("  ❌ Frontend is DOWN or not responding")
    print()

    # Check overall environment
    print("Checking Overall Environment...")
    env_running = await ProcessManager.is_environment_running()
    if env_running:
        print("  ✅ Environment is READY for screenshot capture")
    else:
        print("  ❌ Environment is NOT READY")
        print("     One or more services are not responding")
    print()

    # Check process manager state
    print("Process Manager State:")
    print(f"  Backend process tracked: {ProcessManager._backend_process is not None}")
    print(f"  Frontend process tracked: {ProcessManager._frontend_process is not None}")
    print()

    print("=" * 80)
    if env_running:
        print("✅ All systems GO! You can run get_screenshots now.")
    else:
        print("❌ Environment not ready. Please start services:")
        if not backend_healthy:
            print("   - Backend: cd /Users/tgartner/git/A12-AI-Theming && gradle noClientComposeUp")
        if not frontend_healthy:
            print("   - Frontend: cd /Users/tgartner/git/A12-AI-Theming/client && npm start")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
