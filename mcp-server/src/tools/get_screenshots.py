"""get_screenshots tool implementation.

This tool captures UI screenshots for comparison with target designs.
"""

import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.constants import SCREENSHOTS_DIR

logger = logging.getLogger(__name__)


async def get_screenshots_handler(input_data):
    """Handle get_screenshots tool calls.

    Steps:
    1. Verify environment is running
    2. Determine current round number
    3. Initialize Playwright browser
    4. Execute screenshot workflow:
       - Navigate to login page
       - Take screenshot (ROUNDXX_01.png)
       - Enter credentials and submit
       - Wait for main page load
       - Select customer theme
       - Take screenshot (ROUNDXX_02.png)
       - Click "Create Person" button
       - Fill form with random data
       - Take screenshot (ROUNDXX_03.png)
       - Click Save button
       - Wait for list page
       - Take screenshot (ROUNDXX_04.png)
    5. Close browser
    6. Return screenshot paths and round number

    Args:
        input_data: GetScreenshotsInput instance

    Returns:
        GetScreenshotsOutput instance
    """
    # Import output schema
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from server import GetScreenshotsOutput

    customer_name = input_data.customer_name

    logger.info(f"Capturing screenshots for customer: {customer_name}")

    # Import services
    from services.browser_automation import BrowserAutomation
    from services.process_manager import ProcessManager

    try:
        # 1. Verify environment is running
        if not await ProcessManager.is_environment_running():
            return GetScreenshotsOutput(
                success=False,
                round_number=0,
                screenshots=[],
                screenshots_dir="",
                message="Environment is not running. Please create environment first using create_environment tool."
            )

        # 2. Determine current round number
        screenshots_path = SCREENSHOTS_DIR / customer_name
        screenshots_path.mkdir(parents=True, exist_ok=True)
        round_number = BrowserAutomation.get_next_round_number(screenshots_path)
        screenshots_dir = str(screenshots_path)

        logger.info(f"Starting screenshot capture for round {round_number}")

        # 3. Run browser automation workflow
        async with BrowserAutomation() as automation:
            success, screenshot_paths = await automation.run_screenshot_workflow(
                customer_name=customer_name,
                round_number=round_number
            )

            if not success:
                return GetScreenshotsOutput(
                    success=False,
                    round_number=round_number,
                    screenshots=screenshot_paths,
                    screenshots_dir=screenshots_dir,
                    message=f"Screenshot workflow failed. Captured {len(screenshot_paths)}/4 screenshots."
                )

            return GetScreenshotsOutput(
                success=True,
                round_number=round_number,
                screenshots=screenshot_paths,
                screenshots_dir=screenshots_dir,
                message=f"Successfully captured {len(screenshot_paths)} screenshots for round {round_number}"
            )

    except Exception as e:
        logger.error(f"Error capturing screenshots: {e}", exc_info=True)
        return GetScreenshotsOutput(
            success=False,
            round_number=0,
            screenshots=[],
            screenshots_dir="",
            message=f"Error capturing screenshots: {str(e)}"
        )
