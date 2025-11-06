"""create_environment tool implementation.

This tool sets up the development environment for a customer theme.
"""

import logging
import re
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.constants import (
    SCREENSHOTS_DIR,
    THEMES_DIR,
    BASE_THEME_FILE,
    FRONTEND_URL,
)

logger = logging.getLogger(__name__)


def validate_customer_name(customer_name: str) -> bool:
    """Validate customer name (alphanumeric only, no spaces)."""
    pattern = r'^[a-zA-Z0-9_-]+$'
    return bool(re.match(pattern, customer_name))


async def create_environment_handler(input_data):
    """Handle create_environment tool calls.

    Steps:
    1. Validate customer name
    2. Check if environment is already running
    3. Create theme file
    4. Create screenshots directory
    5. Initialize round counter
    6. Start backend services
    7. Wait for backend health check
    8. Start frontend
    9. Wait for frontend health check
    10. Return success status

    Args:
        input_data: CreateEnvironmentInput instance

    Returns:
        CreateEnvironmentOutput instance
    """
    # Import output schema
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from server import CreateEnvironmentOutput

    customer_name = input_data.customer_name

    # Validate customer name
    if not validate_customer_name(customer_name):
        return CreateEnvironmentOutput(
            success=False,
            theme_path="",
            screenshots_dir="",
            current_round=0,
            frontend_url="",
            message=f"Invalid customer name: {customer_name}. Use alphanumeric characters, hyphens, and underscores only."
        )

    logger.info(f"Creating environment for customer: {customer_name}")

    # Import services
    from services.theme_manager import ThemeManager
    from services.process_manager import ProcessManager
    from services.browser_automation import BrowserAutomation

    try:
        # 1. Create theme file (always, even if environment is running)
        logger.info("Ensuring theme file exists...")
        theme_path_obj = ThemeManager.create_theme_file(customer_name)
        theme_path = str(theme_path_obj)
        logger.info(f"Theme file at: {theme_path}")

        # 2. Create screenshots directory (always, even if environment is running)
        logger.info("Ensuring screenshots directory exists...")
        screenshots_path = SCREENSHOTS_DIR / customer_name
        screenshots_path.mkdir(parents=True, exist_ok=True)
        screenshots_dir = str(screenshots_path)
        logger.info(f"Screenshots directory at: {screenshots_dir}")

        # 3. Initialize round counter
        current_round = BrowserAutomation.get_next_round_number(screenshots_path)
        logger.info(f"Current round: {current_round}")

        # Check if environment is already running
        if await ProcessManager.is_environment_running():
            logger.warning("Environment is already running")
            return CreateEnvironmentOutput(
                success=True,
                theme_path=theme_path,
                screenshots_dir=screenshots_dir,
                current_round=current_round,
                frontend_url=FRONTEND_URL,
                message=f"Environment already running for {customer_name}. Theme file and screenshots directory verified."
            )

        # 4. Start backend services (async, don't wait for full startup)
        logger.info("Starting backend services...")
        # Start the backend process without waiting for health check
        import asyncio
        asyncio.create_task(ProcessManager.start_backend())
        logger.info("Backend services starting in background...")

        # 5. Start frontend (async, don't wait for full startup)
        logger.info("Starting frontend development server...")
        asyncio.create_task(ProcessManager.start_frontend())
        logger.info("Frontend starting in background...")

        # Return immediately - services will continue starting
        # The get_screenshots tool will verify they're running before use
        return CreateEnvironmentOutput(
            success=True,
            theme_path=theme_path,
            screenshots_dir=screenshots_dir,
            current_round=current_round,
            frontend_url=FRONTEND_URL,
            message=(
                f"Environment setup initiated for {customer_name}. "
                f"Theme file and screenshots directory created. "
                f"Backend and frontend services are starting (this may take 1-2 minutes). "
                f"Use get_screenshots to verify services are ready and capture screenshots."
            )
        )

    except Exception as e:
        logger.error(f"Error creating environment: {e}", exc_info=True)
        return CreateEnvironmentOutput(
            success=False,
            theme_path="",
            screenshots_dir="",
            current_round=0,
            frontend_url="",
            message=f"Error creating environment: {str(e)}"
        )
