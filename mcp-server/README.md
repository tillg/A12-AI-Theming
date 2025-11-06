# A12 Theme MCP Server

An MCP (Model Context Protocol) server that automates theme development workflow for A12 applications.

- [A12 Theme MCP Server](#a12-theme-mcp-server)
  - [Features](#features)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Running the Server](#running-the-server)
  - [Testing with MCP Inspector](#testing-with-mcp-inspector)
    - [Quick Setup](#quick-setup)
    - [Troubleshooting](#troubleshooting)
    - [Stopping Services](#stopping-services)
  - [Usage with Claude Code](#usage-with-claude-code)
  - [Prompt](#prompt)
  - [Screenshot Directory Structure](#screenshot-directory-structure)
  - [Development](#development)
    - [Project Structure](#project-structure)
    - [Running Tests](#running-tests)
  - [Workflow Example](#workflow-example)
  - [Troubleshooting](#troubleshooting-1)
    - [Port Conflicts](#port-conflicts)
    - [Frontend Startup Timeout](#frontend-startup-timeout)
    - [Browser Issues](#browser-issues)
  - [License](#license)

## Features

- **create_environment**: Set up development environment for customer themes
  - Starts backend services (Docker Compose + Gradle)
  - Creates theme file from template
  - Starts frontend development server
  - Prepares screenshot directory structure

- **get_screenshots**: Automated UI screenshot capture
  - Navigates through login workflow
  - Applies customer theme
  - Captures screenshots at key UI states
  - Saves with organized naming convention (ROUNDXX_YY.png)

## Requirements

- Python 3.11+
- Node.js 22+ and npm 10.7+
- Gradle 8.5+
- Docker and Docker Compose
- Chromium browser (installed via Playwright)

## Installation

1. Create a virtual environment:
```bash
cd mcp-server
python3 -m venv .venv
source .venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:
```bash
playwright install chromium
```

## Configuration

The server uses the following default configuration (can be overridden with environment variables):

- `FRONTEND_URL`: http://localhost:8081
- `BACKEND_URL`: http://localhost:8082
- `DEFAULT_USERNAME`: admin
- `DEFAULT_PASSWORD`: A12PT-admintest
- `HEADLESS`: false (default - browser is visible; set to true to hide browser for faster execution)

Create a `.env` file in the mcp-server directory to override defaults:

```env
FRONTEND_URL=http://localhost:8081
BACKEND_URL=http://localhost:8082
DEFAULT_USERNAME=admin
DEFAULT_PASSWORD=A12PT-admintest
HEADLESS=false
SLOW_MO=100
```

## Running the Server

Start the MCP server:

```bash
cd mcp-server
python src/server.py

# Then do this in every terminal you use
source .venv/bin/activate 
```

The server communicates via stdio and is designed to be used with MCP clients like Claude Code.

## Testing with MCP Inspector

### Quick Setup

**Note:** `create_environment` will attempt to start backend/frontend automatically, but it's recommended to start them manually first to ensure they're ready.

1. **Start services** (in separate terminals):
   ```bash
   # Terminal 1: Backend (or let create_environment start it)
   gradle noClientComposeUp

   # Terminal 2: Frontend (or let create_environment start it)
   cd client 
   npm start

   # Terminal 3: Verify A12 services are up
   cd mcp-server
   python check_a12_services.py

   # Terminal 4: Inspector
   npx @modelcontextprotocol/inspector

   # Terminal 5: Monitor logs
   cd mcp-server
   tail -f /tmp/mcp-server-debug.log
   ```

2. **Configure Inspector UI**:

In the Inspector UI, manually configure:

- **Transport Type**: `STDIO`
- **Command**: `/Users/tgartner/git/A12-AI-Theming/mcp-server/.venv/bin/python`
  (Use your actual path!)
- **Arguments**: `/Users/tgartner/git/A12-AI-Theming/mcp-server/src/server.py`

**Environment Variables** (click to expand):
- `PYTHONPATH` = `/Users/tgartner/git/A12-AI-Theming/mcp-server/src` (required)
- `HEADLESS` = `true` (optional, to hide browser for faster execution - default is visible)
- `SLOW_MO` = `50` (optional, milliseconds to slow down actions)

   **⚠️ CRITICAL - Set Request Timeout:**
   - Click **"Configuration"** (gear icon)
   - Set **"Request Timeout"** to: `100000` (100 seconds)
   - The screenshot workflow takes 25-35 seconds

   Click **"Connect"**.

3. **Test the tools**:
   - `create_environment` with `{"customer_name": "test-demo"}`
   - `get_screenshots` with `{"customer_name": "test-demo"}`
   - Watch browser automation (if HEADLESS=false)
   - Check logs: `tail -f /tmp/mcp-server-debug.log`
   - Verify screenshots in `screenshots/test-demo/ROUND01_*.png`

### Troubleshooting

* **"Request timed out":** Set timeout to 100000ms in Inspector Configuration
* **Browser not visible:** Environment variable `HEADLESS` must be `false` (or omitted - default is visible)
* **No screenshots:** Verify backend/frontend running with `check_a12_services.py`
* **Need to debug:** Run `manual_workflow.py` - same code, shows detailed logs

### Stopping Services

**Stop A12 Application Services (backend/frontend):**

```bash
cd mcp-server
./stop_a12_services.sh
```

Or manually:
```bash
# Stop frontend
pkill -f "npm start"

# Stop backend/docker
cd /path/to/A12-AI-Theming
gradle composeDown
```

**Stop MCP Server (if running standalone):**

```bash
cd mcp-server
./stop_mcp_server.sh
```

Verify all stopped:
```bash
cd mcp-server
python check_a12_services.py
```

## Usage with Claude Code

Add this server to your Claude Code MCP configuration:

```json
{
  "mcpServers": {
    "a12-theme": {
      "command": "python",
      "args": ["/path/to/mcp-server/src/server.py"],
      "cwd": "/path/to/A12-AI-Theming"
    }
  }
}
```

For claude code on the command line:

```bash
    claude mcp add  --transport stdio a12-theme /Users/tgartner/git/A12-AI-Theming/mcp-server/.venv/bin/python  /Users/tgartner/git/A12-AI-Theming/mcp-server/src/server.py --scope local
```

## Prompt

```text
You are a Web Designer in. charge of styling a prototype application so it matches the client's look & feel.
The client in question is AMAZON.

In order to style the app you are supposed to edit the themes file client/src/themes/<CLIENT>.json. EDIT ONLY THIS FILE!!

Your work environment is already up & running.

Your work process looks the following:
- Execute the get_screenshots tool for your client withe the a12-theme mcp server. Wait 30 seconds so the screenshots can be made.
- Go in the directors screenshots/<CLIENT> and look at the screenshot files: TARGET_XX.png is the design we want to achieve, ROUNDYY_XX.png are the screenshots of the different rounds that you made. 
- Compare the images and think of how you want to change the theme file <CLIENT>.json. 
- Edit <CLIENT>.json
- This triggers a build process. Wait 10 seconds, so the build process finishes.
- Then start over this process.

Make sure you look at all the aspects:
- The colors
- The fonts
- The spacing
- The lines

Besides the look & feel of the CLIENT design you also have to keep the design usable: text must be legible, contrasts must be high enough.

Make as many rounds as you think are helpful. Stop latest after 10 rounds. 

Here's an extract from the webpage that explains our theming system: 
Theming
The theme specifies color of the components, darkness of the surfaces, level of shadow, appropriate opacity of ink elements, etc.

Themes let you apply a consistent tone to your app. It allows you to customize all design aspects of your project in order to meet the specific needs of your business or brand.

You can check the difference between the themes by toggling the "Theme Selector" button positioned on the top-right of our Showcase.

Theme variables
The base Widgets theme includes the following themable aspects:

.colors
This property defines the color palette of the Theme object.

.typography
This property defines the variables related to the Font of the Theme object, including Font Family, Font Size and Font Weight.

.spacing
This property defines the variables related to the Spacing of the Theme object.

.applicationStyles
This property defines the variables related to the overall styles of the Theme object, including shared input styles, label styles, and responsive breakpoints.

.focusStyles
This property defines the variables related to the focus styles of the Theme object.

.divisionLineStyles
This property defines the variables related to the styles of the dividers of the Theme object, including bottomLine, initialLine, topLine and lineHeight.

.baseInputStyles
This property defines the variables related to the Box-Shadow and Line Height styles of the input components inside the Theme object.

.components
This property defines the styling variables related to each of the Widget's component. Each of our Component showcase includes a Theme Configuration section for you to take a deeper look on each component's styling configuration values.
```

## Screenshot Directory Structure

Screenshots are organized in `/screenshots/<CUSTOMER>/`:

```
screenshots/
├── customer1/
│   ├── TARGET_01.png          # Manual: target design reference
│   ├── TARGET_02.png
│   ├── ROUND01_01.png         # Auto: first iteration screenshots
│   ├── ROUND01_02.png
│   ├── ROUND02_01.png         # Auto: second iteration screenshots
│   └── ...
```

## Development

### Project Structure

```
mcp-server/
├── src/
│   ├── server.py                    # MCP server entry point
│   ├── tools/
│   │   ├── create_environment.py    # Environment setup tool
│   │   └── get_screenshots.py       # Screenshot capture tool
│   ├── services/
│   │   ├── process_manager.py       # Process lifecycle management
│   │   ├── browser_automation.py    # Playwright automation
│   │   └── theme_manager.py         # Theme file operations
│   └── config/
│       └── constants.py             # Configuration constants
├── tests/
└── requirements.txt
```

### Running Tests

```bash
pytest
```

## Workflow Example

1. **Create Environment**:
```python
# MCP client calls create_environment
{
  "customer_name": "acme-corp"
}
# Returns theme path, screenshots dir, frontend URL
```

2. **Capture Screenshots**:
```python
# MCP client calls get_screenshots
{
  "customer_name": "acme-corp"
}
# Returns screenshot paths for ROUND01_01.png through ROUND01_04.png
```

3. **AI Compares & Modifies**:
- AI views TARGET_XX.png and ROUNDXX_YY.png screenshots
- AI modifies `client/src/themes/acme-corp.json`
- Theme hot-reloads automatically

4. **Iterate**:
- Call `get_screenshots` again
- New round (ROUND02_XX.png) is created
- Compare and repeat until theme matches target

## Troubleshooting

### Port Conflicts
If ports 8081 or 8082 are in use, stop existing services or configure different ports.

### Frontend Startup Timeout
Frontend may take 30-60 seconds to start. Increase `FRONTEND_STARTUP_TIMEOUT` if needed.

### Browser Issues
If browser automation fails:
- Check that Playwright browsers are installed: `playwright install chromium`
- Try with `HEADLESS=false` to debug visually
- Check browser console logs

## License

See main project LICENSE file.
