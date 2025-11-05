#!/usr/bin/env python3
"""
Manual Playwright workflow for A12 Theme Development.

This script uses THE EXACT SAME CODE as the MCP server (BrowserAutomation class).
You can run this directly to test and debug the automation.

Usage:
    python manual_workflow.py

Configuration:
    Edit the variables at the top of main() to customize.
"""

import asyncio
import sys
import os
import logging
from pathlib import Path

# Configure logging FIRST
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# SET HEADLESS=false BEFORE importing (constants read env vars on import)
os.environ['HEADLESS'] = 'false'
os.environ['SLOW_MO'] = '200'  # Slow down for easier watching

# Add src to path so we can import the services
sys.path.insert(0, str(Path(__file__).parent / "src"))

from services.browser_automation import BrowserAutomation
from config.constants import (
    FRONTEND_URL,
    DEFAULT_USERNAME,
    DEFAULT_PASSWORD,
    SCREENSHOTS_DIR,
)


async def main():
    """Run the complete workflow using the MCP server's BrowserAutomation class."""

    # ============================================================================
    # CONFIGURATION - Edit these values
    # ============================================================================

    USERNAME = DEFAULT_USERNAME
    PASSWORD = DEFAULT_PASSWORD
    CUSTOMER_NAME = "lidl"  # Theme to select (change this to test different themes)
    customer_screenshots_dir = SCREENSHOTS_DIR / CUSTOMER_NAME

    # ============================================================================
    # WORKFLOW START - Uses the SAME BrowserAutomation class as MCP server
    # ============================================================================

    print("=" * 80)
    print("A12 Theme Development - Manual Workflow")
    print("Using BrowserAutomation service (same code as MCP server)")
    print("=" * 80)
    print(f"Frontend URL: {FRONTEND_URL}")
    print(f"Username: {USERNAME}")
    print(f"Theme: {CUSTOMER_NAME}")
    print(f"Screenshots: {customer_screenshots_dir}")
    print("=" * 80)
    print()

    # Create screenshots directory
    customer_screenshots_dir.mkdir(parents=True, exist_ok=True)

    # Determine round number (same logic as MCP server)
    round_number = BrowserAutomation.get_next_round_number(customer_screenshots_dir)
    print(f"Round Number: {round_number}")
    print()

    # Use BrowserAutomation class (same as MCP server)
    async with BrowserAutomation() as automation:
        print("Step 1: Running screenshot workflow...")
        print("  (This uses the exact same code as the MCP server)")
        print()

        # Call the same method the MCP server calls
        success, screenshot_paths = await automation.run_screenshot_workflow(
            customer_name=CUSTOMER_NAME,
            round_number=round_number
        )

        print()
        print("=" * 80)
        if success:
            print("✅ Workflow completed successfully!")
            print(f"Captured {len(screenshot_paths)} screenshots:")
            for path in screenshot_paths:
                print(f"  - {Path(path).name}")
        else:
            print("⚠️  Workflow completed with issues")
            print(f"Captured {len(screenshot_paths)}/{4} screenshots:")
            for path in screenshot_paths:
                print(f"  - {Path(path).name}")

        print(f"Directory: {customer_screenshots_dir}")
        print("=" * 80)
        print()
        print("Press Enter to close browser...")
        input()


if __name__ == "__main__":
    asyncio.run(main())
