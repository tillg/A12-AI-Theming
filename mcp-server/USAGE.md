# MCP Server Usage Guide

## Quick Start

### 1. Install and Setup

```bash
cd mcp-server

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### 2. Configure Claude Code

Add this MCP server to your Claude Code configuration. Edit your Claude Code MCP settings:

**Location**: `~/.claude/config.json` (or similar, depending on your setup)

```json
{
  "mcpServers": {
    "a12-theme": {
      "command": "python",
      "args": [
        "/Users/yourname/git/A12-AI-Theming/mcp-server/src/server.py"
      ],
      "cwd": "/Users/yourname/git/A12-AI-Theming"
    }
  }
}
```

**Important**: Replace `/Users/yourname/git/A12-AI-Theming` with your actual project path.

### 3. Restart Claude Code

After adding the MCP server configuration, restart Claude Code for the changes to take effect.

## Testing with MCP Inspector (Recommended for Development)

Before integrating with Claude Code, it's highly recommended to test the MCP server using the **MCP Inspector** - an official debugging tool that provides a web-based UI for testing MCP servers.

### Why Use MCP Inspector?

- **Rapid Testing**: Test tools instantly without restarting Claude Code
- **Visual Debugging**: See browser automation in action
- **Protocol Inspection**: View raw MCP messages and responses
- **Schema Validation**: Verify inputs/outputs match tool schemas
- **Isolated Testing**: Test server functionality independently

### Installing MCP Inspector

```bash
npm install -g @modelcontextprotocol/inspector
```

### Testing Your MCP Server

1. **Configure the Inspector**:

   A config file has been created at `mcp-server/inspector-config.json`. Edit it with your actual paths:
   ```json
   {
     "mcpServers": {
       "a12-theme": {
         "command": "/path/to/.venv/bin/python",
         "args": ["/path/to/mcp-server/src/server.py"],
         "cwd": "/path/to/A12-AI-Theming",
         "env": {
           "HEADLESS": "false"
         }
       }
     }
   }
   ```

2. **Start the Inspector**:
   ```bash
   cd mcp-server
   npx @modelcontextprotocol/inspector inspector-config.json
   ```

   Or if you installed it globally:
   ```bash
   cd mcp-server
   mcp-inspector inspector-config.json
   ```

3. **Open the Inspector UI**:
   - The Inspector automatically opens your browser at http://localhost:5173
   - You'll see a dashboard with your server's tools listed

4. **Test `create_environment` Tool**:
   - Select `create_environment` from the tools list
   - Fill in the parameters:
     ```json
     {
       "customer_name": "test-demo"
     }
     ```
   - Click "Execute Tool"
   - Watch the console output as the server:
     - Creates the theme file
     - Starts backend services (Gradle + Docker)
     - Starts frontend (npm)
     - Runs health checks
   - View the response with paths and status

5. **Test `get_screenshots` Tool**:
   - Ensure the environment from step 4 is still running
   - Select `get_screenshots` from the tools list
   - Fill in the parameters:
     ```json
     {
       "customer_name": "test-demo"
     }
     ```
   - Click "Execute Tool"
   - With `HEADLESS=false`, watch the browser:
     - Navigate to login page
     - Fill credentials and login
     - Select theme
     - Create and fill person form
     - Save and navigate to list
   - View the response with screenshot paths
   - Check that screenshots were created in `screenshots/test-demo/ROUND01_*.png`

6. **Debug and Iterate**:
   - View server logs in the Inspector console
   - Check request/response details
   - Modify code and restart Inspector to test changes
   - Set `HEADLESS=false` to watch browser automation

### Inspector Pro Tips

- **Watch Browser Automation**: Set `HEADLESS=false` in your `.env` file to see Playwright in action
- **Multiple Rounds**: Call `get_screenshots` multiple times to test round number increment
- **Error Testing**: Test with invalid customer names or when environment isn't running
- **Performance Monitoring**: Watch startup times and health check durations in logs

### Common Inspector Issues

**Port Already in Use (5173)**:
```bash
# Kill existing Inspector process
pkill -f mcp-inspector
```

**Server Not Starting**:
- Check that virtual environment is activated
- Verify all dependencies are installed
- Check Python path is correct

**Browser Automation Fails**:
- Make sure Playwright browsers are installed: `playwright install chromium`
- Set `HEADLESS=false` to debug visually
- Check frontend/backend are actually running

## Using the MCP Tools

### Tool 1: create_environment

Creates a complete development environment for a customer theme.

**What it does:**
1. Creates a theme file from the default template
2. Creates a screenshots directory for the customer
3. Starts backend services (Gradle + Docker Compose)
4. Starts frontend development server (npm)
5. Waits for all services to become healthy

**Example usage in Claude Code:**

```
Please create an environment for customer "acme-corp"
```

Claude will use the `create_environment` tool with:
```json
{
  "customer_name": "acme-corp"
}
```

**Output:**
```json
{
  "success": true,
  "theme_path": "/path/to/client/src/themes/acme-corp.json",
  "screenshots_dir": "/path/to/screenshots/acme-corp",
  "current_round": 1,
  "frontend_url": "http://localhost:8081",
  "message": "Environment created successfully..."
}
```

### Tool 2: get_screenshots

Captures screenshots of the UI with the current theme applied.

**What it does:**
1. Verifies environment is running
2. Determines the next round number
3. Opens a browser and navigates through the UI:
   - Login page (screenshot 1)
   - Main page with theme applied (screenshot 2)
   - Person creation form (screenshot 3)
   - Person list view (screenshot 4)
4. Saves screenshots as `ROUNDXX_YY.png`

**Example usage in Claude Code:**

```
Please capture screenshots for acme-corp
```

Claude will use the `get_screenshots` tool with:
```json
{
  "customer_name": "acme-corp"
}
```

**Output:**
```json
{
  "success": true,
  "round_number": 1,
  "screenshots": [
    "/path/to/screenshots/acme-corp/ROUND01_01.png",
    "/path/to/screenshots/acme-corp/ROUND01_02.png",
    "/path/to/screenshots/acme-corp/ROUND01_03.png",
    "/path/to/screenshots/acme-corp/ROUND01_04.png"
  ],
  "screenshots_dir": "/path/to/screenshots/acme-corp",
  "message": "Successfully captured 4 screenshots for round 1"
}
```

## Typical AI Theme Development Workflow

### 1. Prepare Target Screenshots

Manually capture or prepare target design screenshots and place them in:
```
screenshots/acme-corp/TARGET_01.png
screenshots/acme-corp/TARGET_02.png
screenshots/acme-corp/TARGET_03.png
```

### 2. Start Development Session with Claude

```
I want to develop a theme for "acme-corp" that matches the target screenshots
in screenshots/acme-corp/TARGET_*.png
```

### 3. Claude Creates Environment

Claude will call `create_environment("acme-corp")` which:
- Creates `client/src/themes/acme-corp.json`
- Creates `screenshots/acme-corp/` directory
- Starts all services

### 4. Claude Captures Initial Screenshots

Claude will call `get_screenshots("acme-corp")` which creates:
- `ROUND01_01.png` through `ROUND01_04.png`

### 5. Claude Compares Screenshots

Claude can now:
- View `TARGET_*.png` files (your desired design)
- View `ROUND01_*.png` files (current iteration)
- Compare them visually

### 6. Claude Modifies Theme

Based on the comparison, Claude will edit:
```
client/src/themes/acme-corp.json
```

The frontend will hot-reload with the new theme.

### 7. Iterate

Claude calls `get_screenshots("acme-corp")` again, which creates:
- `ROUND02_01.png` through `ROUND02_04.png`

This cycle continues until the theme closely matches the target.

## Environment Variables

Create a `.env` file in the `mcp-server/` directory to override defaults:

```env
# Frontend URL (default: http://localhost:8081)
FRONTEND_URL=http://localhost:8081

# Backend URL (default: http://localhost:8082)
BACKEND_URL=http://localhost:8082

# Test credentials
DEFAULT_USERNAME=admin
DEFAULT_PASSWORD=A12PT-admintest

# Browser automation settings
HEADLESS=false          # Set to false to watch automation
SLOW_MO=100            # Milliseconds to slow down actions
```

## Troubleshooting

### "Environment is not running"

If you get this error when calling `get_screenshots`:
1. First call `create_environment` to start services
2. Wait for services to become healthy (may take 30-60 seconds)

### Port Already in Use

If ports 8081 or 8082 are already in use:
1. Stop existing services
2. Or configure different ports in `.env`

### Browser Automation Fails

1. Check that Playwright is installed: `playwright install chromium`
2. Set `HEADLESS=false` in `.env` to watch the browser
3. Check browser console logs for errors

### Frontend Takes Too Long to Start

The frontend can take 30-60 seconds to start. If it times out:
1. Increase `FRONTEND_STARTUP_TIMEOUT` in `src/config/constants.py`
2. Check `npm start` works manually in the `client/` directory

### Theme Selectors Not Found

The browser automation looks for theme selectors based on common patterns. If your UI uses different selectors:
1. Update `browser_automation.py` selectors
2. Run with `HEADLESS=false` to see what elements exist
3. Use browser dev tools to identify correct selectors

## Advanced Usage

### Running Without Claude Code

You can test the MCP server directly using stdio:

```bash
cd mcp-server
python src/server.py
```

Then send MCP protocol messages via stdin.

### Manual Testing

For development and testing, you can import and use the services directly:

```python
import asyncio
from src.services.process_manager import ProcessManager
from src.services.browser_automation import BrowserAutomation

async def test():
    # Start services
    await ProcessManager.start_backend()
    await ProcessManager.start_frontend()

    # Capture screenshots
    async with BrowserAutomation() as automation:
        success, paths = await automation.run_screenshot_workflow(
            customer_name="test",
            round_number=1
        )

    # Cleanup
    await ProcessManager.cleanup_all()

asyncio.run(test())
```

## Support

For issues and questions, see the main project documentation or create an issue in the project repository.
