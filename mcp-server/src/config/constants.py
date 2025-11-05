"""Configuration constants for MCP server."""

from pathlib import Path
import os

# Project root directory (parent of mcp-server/)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.resolve()

# URLs
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8081")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8082")

# Test credentials (from CLAUDE.md)
DEFAULT_USERNAME = os.getenv("DEFAULT_USERNAME", "admin")
DEFAULT_PASSWORD = os.getenv("DEFAULT_PASSWORD", "A12PT-admintest")

TEST_USERS = {
    "admin": "A12PT-admintest",
    "user1": "A12PT-user1test",
    "user2": "A12PT-user2test",
}

# Paths
SCREENSHOTS_DIR = PROJECT_ROOT / "screenshots"
CLIENT_DIR = PROJECT_ROOT / "client"
THEMES_DIR = CLIENT_DIR / "src" / "themes"
BASE_THEME_FILE = THEMES_DIR / "default.json"

# Screenshot naming patterns
TARGET_PATTERN = "TARGET_{:02d}.png"
ROUND_PATTERN = "ROUND{:02d}_{:02d}.png"
ROUND_REGEX = r"ROUND(\d{2})_\d{2}\.png"

# Timeouts (in seconds)
BACKEND_STARTUP_TIMEOUT = 180  # 3 minutes
FRONTEND_STARTUP_TIMEOUT = 120  # 2 minutes
HEALTH_CHECK_INTERVAL = 5      # Check every 5 seconds
PAGE_LOAD_TIMEOUT = 10000      # 10 seconds for Playwright (in milliseconds) - faster for MCP

# Browser settings
HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"  # Default: visible browser
SLOW_MO = int(os.getenv("SLOW_MO", "50"))  # Slow down by 50ms (reduced for speed)

# Process commands
GRADLE_BACKEND_CMD = ["gradle", "noClientComposeUp"]
NPM_START_CMD = ["npm", "start"]
