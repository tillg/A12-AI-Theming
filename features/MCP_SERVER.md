# Feature: MCP SERVER 

- [Feature: MCP SERVER](#feature-mcp-server)
  - [Screenshot Directory Structure](#screenshot-directory-structure)
  - [Manual process](#manual-process)
    - [1. Starting our environment](#1-starting-our-environment)
    - [2. Make screen shots](#2-make-screen-shots)
    - [3. Compare to target screens](#3-compare-to-target-screens)
    - [4. Modify theme file](#4-modify-theme-file)
  - [MCP server](#mcp-server)
  - [Implementation Plan](#implementation-plan)
    - [Overview](#overview)
    - [Technology Stack](#technology-stack)
    - [Core Dependencies](#core-dependencies)
    - [Project Structure](#project-structure)
    - [Phase 1: MCP Server Foundation](#phase-1-mcp-server-foundation)
    - [Phase 2: Process Management Service](#phase-2-process-management-service)
    - [Phase 3: Theme Management Service](#phase-3-theme-management-service)
    - [Phase 4: Browser Automation Service](#phase-4-browser-automation-service)
    - [Phase 5: Implement MCP Tools](#phase-5-implement-mcp-tools)
      - [Tool 1: create\_environment](#tool-1-create_environment)
      - [Tool 2: get\_screenshots](#tool-2-get_screenshots)
    - [Phase 6: Additional Features (Optional Enhancements)](#phase-6-additional-features-optional-enhancements)
    - [Phase 7: Testing \& Documentation](#phase-7-testing--documentation)
    - [Phase 8: Integration \& Deployment](#phase-8-integration--deployment)
    - [Implementation Order](#implementation-order)
    - [Key Considerations](#key-considerations)
    - [Success Criteria](#success-criteria)
    - [Future Enhancements](#future-enhancements)

Have an AI work on an A12 Theme so it matches a given look & feel, described by one or more screen shots.

The cycle the AI should go thru:

- Compile the code
- Run the code
- Make one or more screen shots of the UI
- Compare it to the given screen shots
- If it resembles really very well, stop here. Otherwise...
- Modify the A12 theme file
- Start over

We will try to provide the means to build, run, screen shot our A12 application by an MCP Server.

## Screenshot Directory Structure

All screenshots are stored in a top-level `/screenshots` directory with the following organization:

```text
screenshots/
├── <CUSTOMER_1>/
│   ├── TARGET_01.png          # Target design screenshot 1
│   ├── TARGET_02.png          # Target design screenshot 2
│   ├── TARGET_03.png          # Target design screenshot 3
│   ├── ROUND01_01.png         # First iteration screenshot 1
│   ├── ROUND01_02.png         # First iteration screenshot 2
│   ├── ROUND01_03.png         # First iteration screenshot 3
│   ├── ROUND02_01.png         # Second iteration screenshot 1
│   ├── ROUND02_02.png         # Second iteration screenshot 2
│   └── ...
└── <CUSTOMER_2>/
    └── ...
```

**Naming Convention:**

- **Target Screenshots**: `TARGET_XX.png` or `TARGET_XX.jpg` - These are the reference designs that we want to achieve
- **Iteration Screenshots**: `ROUNDXX_YY.png` - Where XX is the iteration number (01, 02, 03...) and YY is the screenshot number within that iteration (01, 02, 03...)

**Benefits:**

- All screenshots for a customer are in one directory
- Easy for LLM and MCP client to access and compare all screenshots
- Clear naming shows iteration progress
- Can visually track how the theme evolves toward the target

## Manual process

In order to understand what the AI will do, we start by doing it ourselves manually:

### 1. Starting our environment

As we will only modify client side aspects, we run all the backend services in a docker compose, and then build & run the frontend in a different process / terminal:

```bash
# Start all backend processes
gradle noClientComposeUp
```

And in a different terminal:

```bash
# Start frontend
cd client
npm start
```

We will give our session a name, i.e. the customer name for which we are creating the theme. Let's call it <CUSTOMER> here.

### 2. Make screen shots 

In order to have relevant screens we need to

* Go to login page 
* Enter credentials - SNAP
* Click ENTER
* See the first screen 
* Select the theme we are working on in the theme selector (<CUSTOMER>)
* Create a new person with the `+` button
* Enter random data - SNAP
* press SAVE
* We're back at the list - SNAP

### 3. Compare to target screens

Easy for us humans: Put the screen shots and the target screens side by side and look at them...

### 4. Modify theme file

Less easy for us: Go to the file `client/src/themes/<CUSTOMER>`.json and edit stuff and save it.

## MCP server

In order to enable an LLM to run & control the above process, these are the operations our MCP server should provide:

* `create_environment(<CUSTOMER>)` Set up the environment for a new customer, which basically consists of:
  * Start the backend services as docker compose
  * Copying a starting point of a theme file to `client/src/themes/<CUSTOMER>.json`
  * Run `npm start`
  * Create the `screenshots/<CUSTOMER>/` directory if it doesn't exist
  * Determine the next round number for screenshots
* `get_screenshots(<CUSTOMER>)` Create screenshots and save them to `screenshots/<CUSTOMER>/` with naming convention:
  * Determine next ROUNDXX number by scanning existing files
  * Navigate through UI and capture 4 screenshots: ROUNDXX_01.png through ROUNDXX_04.png
  * Return paths to all generated screenshots

Besides these MCP Server tools, all the LLM needs to be able to do is:

* **Looking at picture files** - The LLM can access all files in `screenshots/<CUSTOMER>/` directory to compare:
  * TARGET_XX.png files (placed manually by user) - the desired design goal
  * ROUNDXX_YY.png files (generated by MCP server) - current iteration results
* **Edit & save the theme JSON file** - The LLM can edit `client/src/themes/<CUSTOMER>.json` to adjust theme settings

These file operations can probably be made available with an off-the-shelf MCP server (file system MCP server).

---

## Implementation Plan

### Overview

Build a custom MCP (Model Context Protocol) server in Python that provides tools for automated theme development. The server will manage environment lifecycle, automate UI interactions, and capture screenshots for comparison.

### Technology Stack

- **MCP SDK**: `mcp` Python package for MCP server implementation
- **Browser Automation**: Playwright for Python (supports multiple browsers, better for modern web apps)
- **Process Management**: Python `subprocess` module for managing Gradle and npm processes
- **Language**: Python 3.11+ for modern features and type hints
- **Dependency Management**: Poetry or pip with requirements.txt

### Core Dependencies

```text
mcp>=0.1.0                  # MCP SDK for Python
playwright>=1.40.0          # Browser automation
pydantic>=2.0.0             # Data validation and settings
aiofiles>=23.0.0            # Async file operations
faker>=20.0.0               # Generate random test data
python-dotenv>=1.0.0        # Environment variable management
pyyaml>=6.0                 # YAML configuration (optional)
pytest>=7.0.0               # Testing framework
pytest-asyncio>=0.21.0      # Async test support
```

### Project Structure

```text
mcp-server/
├── pyproject.toml              # Poetry configuration (or requirements.txt)
├── README.md
├── src/
│   ├── __init__.py
│   ├── server.py               # MCP server entry point
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── create_environment.py    # Environment setup tool
│   │   └── get_screenshots.py       # Screenshot automation tool
│   ├── services/
│   │   ├── __init__.py
│   │   ├── process_manager.py       # Manage Gradle/npm processes
│   │   ├── browser_automation.py    # Playwright automation logic
│   │   └── theme_manager.py         # Theme file operations
│   └── config/
│       ├── __init__.py
│       └── constants.py             # URLs, credentials, paths
└── tests/
    └── __init__.py
```

### Phase 1: MCP Server Foundation

**Tasks:**

1. Initialize Python project in `mcp-server/` directory
2. Install dependencies:
   - `mcp` - MCP SDK for Python
   - `playwright` - Browser automation
   - `aiofiles` - Async file operations
   - `pydantic` - Data validation and settings management
3. Set up Poetry/pip configuration (`pyproject.toml` or `requirements.txt`)
4. Install Playwright browsers: `playwright install chromium`
5. Set up MCP server with basic structure using the Python MCP SDK
6. Define tool schemas for `create_environment` and `get_screenshots`
7. Create configuration management in `config/constants.py` for:
   - Frontend URL (<http://localhost:8081>)
   - Backend URL (<http://localhost:8082>)
   - Test credentials (admin/user credentials from CLAUDE.md)
   - Screenshot base directory (`screenshots/` at project root)
   - Base theme template path
   - Screenshot naming patterns (TARGET_XX.png, ROUNDXX_YY.png)

### Phase 2: Process Management Service

**Tasks:**

1. Implement `process_manager.py` with:
   - `start_backend()`: Execute `gradle noClientComposeUp` using `subprocess.Popen` and track process
   - `start_frontend()`: Execute `npm start` in client directory using `subprocess.Popen` and track process
   - `stop_backend()`: Gracefully terminate backend services using process signals
   - `stop_frontend()`: Kill frontend process
   - `is_healthy()`: Check if services are responding via HTTP health checks
2. Add process tracking using class attributes to prevent duplicate starts
3. Implement cleanup handlers for graceful shutdown using `atexit` and signal handlers
4. Add timeout and retry logic for service startup using `asyncio`
5. Use `asyncio.create_subprocess_exec` for async process management

### Phase 3: Theme Management Service

**Tasks:**

1. Implement `theme_manager.py` with:
   - `create_theme_file(customer_name: str) -> str`: Copy base theme to `client/src/themes/<CUSTOMER>.json`
   - `validate_theme_file(theme_path: str) -> bool`: Validate JSON structure using `json.load()`
   - `get_theme_path(customer_name: str) -> Path`: Return absolute path to theme file using `pathlib.Path`
2. Create base theme template (if needed) or identify existing template to copy
3. Add theme file registration logic (if themes need to be registered in code)
4. Use `shutil.copy2()` for file copying operations

### Phase 4: Browser Automation Service

**Tasks:**

1. Implement `browser_automation.py` with async methods:
   - `setup_browser() -> Browser`: Initialize Playwright browser instance using `async with`
   - `navigate_to_login(page: Page)`: Navigate to <http://localhost:8081>
   - `login(page: Page, username: str, password: str)`: Fill credentials and submit
   - `select_theme(page: Page, theme_name: str)`: Click theme selector and choose theme
   - `create_new_person(page: Page)`: Click + button and navigate to form
   - `fill_person_form(page: Page)`: Enter random test data using `faker` library
   - `save_and_return(page: Page)`: Submit form and return to list
   - `capture_screenshot(page: Page, path: Path)`: Take screenshot and save to specified path
   - `close_browser(browser: Browser)`: Clean up browser instance
   - `get_next_round_number(customer_dir: Path) -> int`: Scan directory for existing ROUNDXX files and return next number
2. Use Playwright's built-in wait strategies (`page.wait_for_selector()`, `page.wait_for_load_state()`)
3. Implement error handling for missing elements or timeouts using try/except blocks
4. Add screenshot comparison utilities (optional for future enhancement)
5. Use async/await pattern throughout for better performance

### Phase 5: Implement MCP Tools

#### Tool 1: create_environment

**Input Schema:**

```python
from pydantic import BaseModel, Field

class CreateEnvironmentInput(BaseModel):
    customer_name: str = Field(..., description="Name of the customer/theme")
```

**Implementation Steps:**

1. Validate customer name (alphanumeric, no spaces) using regex
2. Check if environment is already running
3. Create theme file by copying `default.json` to `<CUSTOMER>.json`
4. Create screenshots directory: `screenshots/<CUSTOMER>/` (if it doesn't exist)
5. Initialize round counter (check existing ROUNDXX files and increment)
6. Start backend services using `process_manager.start_backend()`
7. Wait for backend health check (retry with timeout using `asyncio`)
8. Start frontend using `process_manager.start_frontend()`
9. Wait for frontend health check (retry with timeout using `asyncio`)
10. Return success status with environment details

**Output:**

```python
from pydantic import BaseModel

class CreateEnvironmentOutput(BaseModel):
    success: bool
    theme_path: str
    screenshots_dir: str  # Path to screenshots/<customer_name>/
    current_round: int    # Next round number to use
    frontend_url: str
    message: str
```

#### Tool 2: get_screenshots

**Input Schema:**

```python
from pydantic import BaseModel, Field

class GetScreenshotsInput(BaseModel):
    customer_name: str = Field(..., description="Must match existing environment")
```

**Implementation Steps:**

1. Verify environment is running
2. Determine current round number by checking existing `ROUNDXX_*` files in `screenshots/<customer_name>/`
3. Initialize Playwright browser (headless mode) using async context manager
4. Execute screenshot workflow:
   - Navigate to login page
   - Take screenshot: `screenshots/<customer_name>/ROUNDXX_01.png` (login page)
   - Enter credentials and submit
   - Wait for main page load
   - Select customer theme from theme selector
   - Take screenshot: `screenshots/<customer_name>/ROUNDXX_02.png` (theme applied)
   - Click "Create Person" button (+)
   - Fill form with random data (first name, last name, email, etc.)
   - Take screenshot: `screenshots/<customer_name>/ROUNDXX_03.png` (person form)
   - Click Save button
   - Wait for list page
   - Take screenshot: `screenshots/<customer_name>/ROUNDXX_04.png` (person list)
5. Close browser
6. Return screenshot paths and round number

**Output:**

```python
from pydantic import BaseModel
from typing import List

class GetScreenshotsOutput(BaseModel):
    success: bool
    round_number: int       # Which round these screenshots are from
    screenshots: List[str]  # Absolute paths to ROUNDXX_YY.png files
    screenshots_dir: str    # Path to screenshots/<customer_name>/
    message: str
```

### Phase 6: Additional Features (Optional Enhancements)

1. **destroy_environment Tool**: Clean up environment and stop services
2. **compare_screenshots Tool**: Basic visual comparison between current and target screenshots using `PIL` (Pillow) or `opencv-python`
3. **validate_theme Tool**: Validate theme JSON before applying using JSON schema validation
4. **get_environment_status Tool**: Check current environment state
5. **Logging**: Structured logging using Python's `logging` module with JSON formatting
6. **Configuration File**: External YAML configuration using `pyyaml` for easy configuration updates

### Phase 7: Testing & Documentation

**Tasks:**

1. Manual testing of each tool individually
2. End-to-end testing of the full cycle
3. Add unit tests using `pytest` for core services
4. Document MCP server usage in README.md:
   - Installation instructions (`pip install -r requirements.txt` or `poetry install`)
   - How to start the MCP server (`python src/server.py`)
   - Tool descriptions and parameters
   - Example workflows
5. Add error scenarios and troubleshooting guide
6. Document integration with Claude Code or other MCP clients
7. Create example configuration file

### Phase 8: Integration & Deployment

**Tasks:**

1. Create startup script for MCP server (`start_mcp_server.sh` or `start_mcp_server.bat`)
2. Add MCP server configuration to Claude Code settings (MCP configuration JSON)
3. Set up virtual environment with all dependencies
4. Test with actual LLM workflow
5. Document the AI-assisted theming workflow:
   - How to place TARGET_XX.png files before starting
   - How the LLM compares ROUNDXX files to TARGET files
   - How to iterate on theme changes
6. Create example target screenshots for testing (manually capture or provide samples)
7. Fine-tune timing and waits based on real application behavior
8. Package the MCP server for distribution (optional: create a pip-installable package)
9. Document the directory structure and naming conventions in README

### Implementation Order

**Week 1:**
- Phase 1: MCP Server Foundation
- Phase 2: Process Management Service
- Phase 3: Theme Management Service

**Week 2:**
- Phase 4: Browser Automation Service
- Phase 5: Implement MCP Tools

**Week 3:**
- Phase 6: Additional Features (as needed)
- Phase 7: Testing & Documentation
- Phase 8: Integration & Deployment

### Key Considerations

1. **Process Lifecycle**: Ensure proper cleanup of Gradle/npm processes on errors using signal handlers
2. **Port Conflicts**: Detect if ports 8081/8082 are already in use before starting services
3. **Timing Issues**: Frontend may take 30-60s to start; add appropriate waits using `asyncio.sleep()` and retries
4. **Theme Hot Reload**: Changes to theme files should reflect immediately (verify this with webpack dev server)
5. **Browser State**: Consider keeping browser open between screenshot runs vs. fresh start each time
6. **Credentials Management**: Store test credentials securely using environment variables or `.env` file with `python-dotenv`
7. **Screenshot Storage**: All screenshots stored in `screenshots/<customer>/` directory
   - TARGET_XX files should be manually placed by user before starting
   - ROUNDXX files automatically created and numbered sequentially
   - Implement retention policy to avoid disk space issues (optional)
8. **Round Number Management**: Automatically detect next round number by scanning existing ROUNDXX files
9. **Concurrent Environments**: Initially support one environment at a time using singleton pattern
10. **Error Recovery**: Provide clear error messages and recovery suggestions with Python exceptions
11. **Platform Compatibility**: Test on macOS (current), Linux, and Windows if needed
12. **Python Version**: Require Python 3.11+ for modern async features and type hints
13. **Async/Await**: Use asyncio throughout for better performance with I/O operations
14. **Virtual Environment**: Always run in a virtual environment to avoid dependency conflicts
15. **Screenshot Comparison**: LLM can access all screenshots in customer directory for comparison with targets

### Success Criteria

- ✅ MCP server starts and registers tools successfully
- ✅ `create_environment` starts all services and creates theme file
- ✅ `get_screenshots` navigates UI and captures all required screenshots
- ✅ Screenshots are clear, properly named, and accessible to LLM
- ✅ Theme file changes are reflected in subsequent screenshot runs
- ✅ Graceful error handling and cleanup with proper async context managers
- ✅ Complete documentation for setup and usage
- ✅ All dependencies listed in `requirements.txt` or `pyproject.toml`

### Future Enhancements

1. **Multi-browser Support**: Test themes across Chrome, Firefox, Safari
2. **Responsive Testing**: Capture screenshots at different viewport sizes
3. **Visual Regression Testing**: Automated comparison with target screenshots
4. **Theme Generation**: AI-assisted initial theme generation from target screenshots
5. **Accessibility Testing**: Automated a11y checks on themed UI
6. **Component Isolation**: Screenshot individual components in isolation
