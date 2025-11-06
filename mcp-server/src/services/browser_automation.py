"""Browser automation service using Playwright.

This module handles UI automation for capturing screenshots:
- Browser setup and teardown
- Login workflow
- Theme selection
- Form filling with random data
- Screenshot capture
"""

import logging
import re
from pathlib import Path
from typing import Optional, Tuple

from playwright.async_api import (
    async_playwright,
    Browser,
    Page,
    Playwright,
    TimeoutError as PlaywrightTimeoutError
)
from faker import Faker

from config.constants import (
    FRONTEND_URL,
    DEFAULT_USERNAME,
    DEFAULT_PASSWORD,
    PAGE_LOAD_TIMEOUT,
    HEADLESS,
    SLOW_MO,
    SCREENSHOTS_DIR,
    ROUND_REGEX,
)

logger = logging.getLogger(__name__)
fake = Faker()


class BrowserAutomation:
    """Handles browser automation for UI screenshot capture."""

    def __init__(self):
        """Initialize browser automation."""
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None

    async def __aenter__(self):
        """Context manager entry."""
        await self.setup_browser()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.close_browser()

    async def setup_browser(self) -> Browser:
        """Initialize Playwright and launch browser.

        Returns:
            Browser: Playwright browser instance
        """
        logger.info("Setting up Playwright browser...")

        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=HEADLESS,
                slow_mo=SLOW_MO,
            )

            # Create a new page with timeout settings
            self.page = await self.browser.new_page()
            self.page.set_default_timeout(PAGE_LOAD_TIMEOUT)

            logger.info("Browser setup complete")
            return self.browser

        except Exception as e:
            logger.error(f"Error setting up browser: {e}", exc_info=True)
            await self.close_browser()
            raise

    async def close_browser(self):
        """Close browser and clean up Playwright resources."""
        logger.info("Closing browser...")

        try:
            if self.page:
                await self.page.close()
                self.page = None

            if self.browser:
                await self.browser.close()
                self.browser = None

            if self.playwright:
                await self.playwright.stop()
                self.playwright = None

            logger.info("Browser closed")

        except Exception as e:
            logger.error(f"Error closing browser: {e}", exc_info=True)

    async def navigate_to_login(self) -> bool:
        """Navigate to the login page.

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.page:
            logger.error("Browser page not initialized")
            return False

        try:
            logger.info(f"Navigating to {FRONTEND_URL}...")
            await self.page.goto(FRONTEND_URL, wait_until="domcontentloaded", timeout=15000)

            # Wait for React to render - look for the root div to have content
            logger.info("Waiting for React app to render...")

            # Wait for either login form or main app content
            try:
                # Look for login form specifically (username/password inputs)
                await self.page.wait_for_selector(
                    'input[type="text"], input[type="password"]',
                    timeout=10000
                )
                logger.info("Login form detected")
            except:
                # Or wait for any content in root
                await self.page.wait_for_selector('#root > *', timeout=10000)
                logger.info("App content loaded")

            # Additional wait for any initial redirects or loading
            await self.page.wait_for_timeout(1500)

            logger.info(f"Navigation complete. Current URL: {self.page.url}")
            return True

        except PlaywrightTimeoutError as e:
            logger.error(f"Timeout navigating to login page: {e}")
            return False

        except Exception as e:
            logger.error(f"Error navigating to login page: {e}", exc_info=True)
            return False

    async def login(
        self,
        username: str = DEFAULT_USERNAME,
        password: str = DEFAULT_PASSWORD
    ) -> bool:
        """Fill login form and submit.

        Args:
            username: Username for login
            password: Password for login

        Returns:
            bool: True if login successful, False otherwise
        """
        if not self.page:
            logger.error("Browser page not initialized")
            return False

        try:
            logger.info(f"Logging in as {username}...")

            # Wait for login form to be rendered
            await self.page.wait_for_timeout(1000)

            # Find username field - try multiple selectors
            username_field = None
            username_selectors = [
                'input[name="username"]',
                'input[id="username"]',
                'input[type="text"]',
                'input[placeholder*="name" i]',
            ]

            for selector in username_selectors:
                username_field = await self.page.query_selector(selector)
                if username_field and await username_field.is_visible():
                    logger.info(f"Found username field with: {selector}")
                    break

            if not username_field:
                logger.error("Could not find username field!")
                return False

            # Find password field
            password_field = await self.page.query_selector('input[type="password"]')
            if not password_field or not await password_field.is_visible():
                logger.error("Could not find password field!")
                return False

            logger.info("Found login fields, filling...")

            # Fill username
            await username_field.fill(username)
            logger.info(f"Filled username: {username}")

            # Fill password
            await password_field.fill(password)
            logger.info("Filled password")

            # Submit form (look for submit button or press Enter)
            submit_button = await self.page.query_selector('button[type="submit"], button:has-text("Login"), button:has-text("Sign in")')

            if submit_button:
                await submit_button.click()
            else:
                # Fallback: press Enter
                await self.page.press('input[type="password"]', 'Enter')

            # Wait for navigation after login
            logger.info("Waiting for redirect after login...")
            await self.page.wait_for_load_state("domcontentloaded", timeout=10000)

            # Wait additional time for any redirects to complete
            await self.page.wait_for_timeout(1500)

            # Wait for the main app to be loaded (wait for body or main content)
            try:
                await self.page.wait_for_selector('body', timeout=5000)
                logger.info(f"Current URL after login: {self.page.url}")
            except:
                pass

            logger.info("Login complete")
            return True

        except PlaywrightTimeoutError as e:
            logger.error(f"Timeout during login: {e}")
            return False

        except Exception as e:
            logger.error(f"Error during login: {e}", exc_info=True)
            return False

    async def select_theme(self, theme_name: str) -> bool:
        """Select a theme from the theme selector.

        The theme selector is a popup button in the header with a palette icon.

        Args:
            theme_name: Name of the theme to select

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.page:
            logger.error("Browser page not initialized")
            return False

        try:
            logger.info(f"Selecting theme: {theme_name}")

            # Wait for React app to be fully rendered
            await self.page.wait_for_timeout(1000)

            # Find the theme selector button (has palette icon, not public or account_circle)
            # The theme button has a Material Icon "palette" inside it
            theme_button_selector = 'button.header-trigger:has(i span[aria-hidden="true"]:text("palette"))'

            theme_button = await self.page.query_selector(theme_button_selector)

            if not theme_button:
                # Try alternative: find any button with palette icon
                all_buttons = await self.page.query_selector_all('button.header-trigger')
                for btn in all_buttons:
                    icon_text = await btn.evaluate('el => el.querySelector("i span[aria-hidden]")?.textContent')
                    if icon_text == "palette":
                        theme_button = btn
                        logger.info("Found theme button via icon search")
                        break

            if theme_button and await theme_button.is_visible():
                logger.info("Found theme selector button, clicking to open menu...")
                await theme_button.click()

                # Wait for popup menu to appear
                await self.page.wait_for_timeout(1000)

                # Find theme option (case-insensitive)
                theme_option = await self.page.query_selector(f'text=/{theme_name}/i')

                if theme_option:
                    logger.info(f"Found theme '{theme_name}', clicking...")
                    await theme_option.click()
                    await self.page.wait_for_timeout(1000)
                    logger.info(f"Theme '{theme_name}' selected")
                else:
                    logger.warning(f"Could not find theme '{theme_name}' in menu, continuing anyway")

            else:
                logger.warning("Could not find theme selector button, continuing anyway")

            return True

        except Exception as e:
            logger.error(f"Error selecting theme: {e}", exc_info=True)
            # Don't fail completely if theme selection fails
            logger.warning("Continuing without theme selection")
            return True

    async def create_new_person(self) -> bool:
        """Click the create new person button (+).

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.page:
            logger.error("Browser page not initialized")
            return False

        try:
            logger.info("Looking for 'Create Person' button...")

            # Wait a moment for the page to settle
            await self.page.wait_for_timeout(1000)

            # Based on actual HTML: <button aria-label="Add" ...><span>Add</span></button>
            selectors = [
                'button[aria-label="Add"]',
                'button[data-role="button"]:has-text("Add")',
                'button:has-text("Add")',
                'button:has-text("+")',
                'button:has-text("New")',
                'button:has-text("Create")',
            ]

            button_found = False
            for selector in selectors:
                try:
                    create_button = await self.page.query_selector(selector)
                    if create_button:
                        # Check if visible
                        if await create_button.is_visible():
                            logger.info(f"Found Add button with selector: {selector}")
                            await create_button.click()
                            button_found = True
                            break
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue

            if not button_found:
                # Last resort: try to find any button that looks like it might create
                logger.warning("Could not find create button with known selectors, trying generic search...")
                all_buttons = await self.page.query_selector_all('button, a.button, a[role="button"]')
                logger.info(f"Found {len(all_buttons)} total buttons on page")

                # Log all button texts for debugging
                button_texts = []
                for idx, button in enumerate(all_buttons):
                    try:
                        text = await button.text_content()
                        is_visible = await button.is_visible()
                        if text:
                            text = text.strip()
                            button_texts.append(f"Button {idx}: '{text}' (visible={is_visible})")
                    except:
                        pass

                if button_texts:
                    logger.info("Available buttons: " + ", ".join(button_texts[:10]))  # Show first 10

                # Try to find create button
                for button in all_buttons:
                    try:
                        if not await button.is_visible():
                            continue
                        text = await button.text_content()
                        if text:
                            text_lower = text.strip().lower()
                            if any(word in text_lower for word in ['+', 'add', 'new', 'create', 'hinzufügen', 'neu']):
                                logger.info(f"Found potential create button with text: '{text.strip()}'")
                                await button.click()
                                button_found = True
                                break
                    except Exception as e:
                        logger.debug(f"Error checking button: {e}")
                        continue

            if not button_found:
                logger.error("Could not find create button!")
                # Take a screenshot to help debug
                debug_path = Path("/tmp/debug-no-button.png")
                await self.page.screenshot(path=str(debug_path))
                logger.error(f"Debug screenshot saved to: {debug_path}")
                return False

            # Wait for form to load (use domcontentloaded for speed)
            await self.page.wait_for_load_state("domcontentloaded", timeout=10000)

            logger.info("Create person form opened")
            return True

        except PlaywrightTimeoutError as e:
            logger.error(f"Timeout opening create form: {e}")
            return False

        except Exception as e:
            logger.error(f"Error opening create form: {e}", exc_info=True)
            return False

    async def fill_person_form(self) -> bool:
        """Fill the person form with random test data using Faker.

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.page:
            logger.error("Browser page not initialized")
            return False

        try:
            logger.info("Filling person form with random data...")

            # Wait for React form to fully initialize and be ready for interaction
            # This is critical when running in MCP server context vs manual script
            logger.info("Waiting for form to be fully initialized...")
            await self.page.wait_for_timeout(2000)

            # Generate random data
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = fake.email()
            city = fake.city()
            country = fake.country()
            # Generate birth date for someone between 18 and 80 years old
            birth_date = fake.date_of_birth(minimum_age=18, maximum_age=80)
            # Format as YYYY-MM-DD for HTML date inputs
            birth_date_str = birth_date.strftime('%Y-%m-%d')

            logger.info(f"Generated test data: {first_name} {last_name}, {email}, DOB: {birth_date_str}")

            # Fill form fields using actual field IDs from the A12 form
            # Fields have IDs like: a12-FirstName-F3, a12-LastName-F4, etc.
            fields_to_fill = [
                # (label text or ID pattern, value)
                ('a12-FirstName', first_name),
                ('a12-LastName', last_name),
                ('a12-EmailAddress', email),
                ('a12-DateOfBirth', birth_date_str),  # Birth date in YYYY-MM-DD format
                ('a12-PlaceOfBirth', city),  # Use city for place of birth
                ('a12-Nationality', country),
            ]

            filled_count = 0
            for field_pattern, value in fields_to_fill:
                try:
                    # Find input that has ID containing the pattern
                    selector = f'input[id^="{field_pattern}"]'

                    # Wait for field to be present and visible (with retry)
                    try:
                        await self.page.wait_for_selector(selector, state="visible", timeout=5000)
                    except PlaywrightTimeoutError:
                        logger.warning(f"Field not found after timeout: {field_pattern}")
                        continue

                    field = await self.page.query_selector(selector)

                    if field and await field.is_visible():
                        # Check if it's a date field
                        field_type = await field.get_attribute('type')
                        is_date_field = 'DateOfBirth' in field_pattern or field_type == 'date'

                        # Click field first to ensure it's focused (important for React forms)
                        await field.click()
                        await self.page.wait_for_timeout(200)

                        if is_date_field:
                            # For date fields, use keyboard input which is more reliable
                            # Clear field first using triple-click to select all
                            await field.click(click_count=3)
                            await self.page.wait_for_timeout(100)
                            await field.press('Backspace')
                            await self.page.wait_for_timeout(150)

                            # Type the date value character by character
                            await field.type(value, delay=50)
                            await self.page.wait_for_timeout(200)

                            # Press Tab to trigger validation/blur
                            await field.press('Tab')
                            await self.page.wait_for_timeout(100)
                        else:
                            # For regular fields, use fill method
                            # Clear any existing value
                            await field.fill('')
                            await self.page.wait_for_timeout(100)

                            # Fill with new value
                            await field.fill(value)
                            await self.page.wait_for_timeout(100)

                        # Verify the value was set
                        actual_value = await field.input_value()
                        if actual_value == value or (is_date_field and actual_value):
                            logger.info(f"Filled {field_pattern}: {value}")
                            filled_count += 1
                        else:
                            logger.warning(f"Field {field_pattern} value mismatch: expected '{value}', got '{actual_value}'")
                    else:
                        logger.debug(f"Could not find field: {field_pattern}")

                except Exception as e:
                    logger.warning(f"Error filling {field_pattern}: {e}")
                    continue

            logger.info(f"Filled {filled_count}/{len(fields_to_fill)} fields")

            if filled_count == 0:
                logger.error("No fields were filled! Form may not be ready.")
                return False

            logger.info("Person form filled with test data")
            return True

        except Exception as e:
            logger.error(f"Error filling person form: {e}", exc_info=True)
            return False

    async def save_and_return(self) -> bool:
        """Click save button and return to list view.

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.page:
            logger.error("Browser page not initialized")
            return False

        try:
            logger.info("Saving form and returning to list...")

            # Look for save button
            save_button = await self.page.query_selector(
                'button:has-text("Save"), button:has-text("Submit"), button[type="submit"], [data-testid="save-button"]'
            )

            if save_button:
                await save_button.click()
                logger.info("Clicked Save button")
            else:
                # Fallback: try to submit form
                await self.page.press('input', 'Enter')
                logger.info("Pressed Enter to submit")

            # Wait for save to process and navigate
            logger.info("Waiting for save to complete...")
            await self.page.wait_for_timeout(2000)

            # Wait for navigation back to list
            logger.info("Waiting for navigation back to list...")
            await self.page.wait_for_load_state("domcontentloaded", timeout=10000)

            logger.info("Page loaded after save")

            logger.info("Saved and returned to list view")
            return True

        except PlaywrightTimeoutError as e:
            logger.error(f"Timeout saving form: {e}")
            return False

        except Exception as e:
            logger.error(f"Error saving form: {e}", exc_info=True)
            return False

    async def capture_screenshot(self, path: Path, full_page: bool = True) -> bool:
        """Capture a screenshot and save to the specified path.

        Args:
            path: Path where screenshot should be saved
            full_page: Whether to capture full page or just viewport

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.page:
            logger.error("Browser page not initialized")
            return False

        try:
            # Ensure directory exists
            path.parent.mkdir(parents=True, exist_ok=True)

            # Capture screenshot
            await self.page.screenshot(path=str(path), full_page=full_page)

            logger.info(f"Screenshot saved: {path}")
            return True

        except Exception as e:
            logger.error(f"Error capturing screenshot: {e}", exc_info=True)
            return False

    @staticmethod
    def get_next_round_number(customer_dir: Path) -> int:
        """Scan directory for existing ROUNDXX files and return next round number.

        Args:
            customer_dir: Directory containing customer screenshots

        Returns:
            int: Next round number to use (1 if no rounds exist)
        """
        if not customer_dir.exists():
            logger.info(f"Customer directory doesn't exist yet: {customer_dir}")
            return 1

        try:
            # Find all ROUNDXX files
            max_round = 0
            pattern = re.compile(ROUND_REGEX)

            for file in customer_dir.glob("ROUND*.png"):
                match = pattern.match(file.name)
                if match:
                    round_num = int(match.group(1))
                    max_round = max(max_round, round_num)

            next_round = max_round + 1
            logger.info(f"Next round number for {customer_dir.name}: {next_round}")
            return next_round

        except Exception as e:
            logger.error(f"Error determining next round number: {e}", exc_info=True)
            return 1

    async def run_screenshot_workflow(
        self,
        customer_name: str,
        round_number: int
    ) -> Tuple[bool, list[str]]:
        """Execute the complete screenshot capture workflow.

        Args:
            customer_name: Name of the customer/theme
            round_number: Round number for screenshot naming

        Returns:
            Tuple[bool, list[str]]: (success, list of screenshot paths)
        """
        screenshots = []
        customer_dir = SCREENSHOTS_DIR / customer_name
        customer_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Step 1: Navigate to login
            if not await self.navigate_to_login():
                return False, screenshots

            # Screenshot 1: Login page
            # screenshot_path = customer_dir / f"ROUND{round_number:02d}_01.png"
            # if await self.capture_screenshot(screenshot_path):
            #     screenshots.append(str(screenshot_path))

            # Step 2: Login
            login_success = await self.login()

            # Wait for page to fully settle after login
            logger.info("Waiting for page to fully load after login...")
            await self.page.wait_for_timeout(1000)

            # Take screenshot after login regardless of success
            # logger.info("Taking screenshot after login...")
            # screenshot_path = customer_dir / f"ROUND{round_number:02d}_02.png"
            # if await self.capture_screenshot(screenshot_path):
            #     screenshots.append(str(screenshot_path))

            if not login_success:
                logger.error("Login failed, but continuing to capture what we can...")
                # Return partial results
                return True, screenshots  # Return True so we get partial screenshots

            # Wait for main page to fully load
            logger.info("Waiting for main page to load...")
            await self.page.wait_for_timeout(1500)

            # Try to select theme (don't fail if it doesn't work)
            await self.select_theme(customer_name)

            # Step 3: Create new person
            if not await self.create_new_person():
                logger.warning("Could not create new person, returning screenshots captured so far")
                return True, screenshots  # Return what we have so far

            # Step 4: Fill form
            if not await self.fill_person_form():
                return False, screenshots

            # Brief wait for form to settle after filling
            await self.page.wait_for_timeout(500)

            # Screenshot 3: Person form filled
            screenshot_path = customer_dir / f"ROUND{round_number:02d}_03.png"
            if await self.capture_screenshot(screenshot_path):
                screenshots.append(str(screenshot_path))

            # Step 5: Save and return to list
            if not await self.save_and_return():
                return False, screenshots

            # Brief wait for list to render
            await self.page.wait_for_timeout(500)

            # Screenshot 4: Person list with new entry
            screenshot_path = customer_dir / f"ROUND{round_number:02d}_04.png"
            if await self.capture_screenshot(screenshot_path):
                screenshots.append(str(screenshot_path))

            logger.info(f"Screenshot workflow completed successfully. Captured {len(screenshots)} screenshots.")
            return True, screenshots

        except Exception as e:
            logger.error(f"Error in screenshot workflow: {e}", exc_info=True)
            return False, screenshots
