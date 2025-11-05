"""MCP Server for A12 Theme Development Automation.

This server provides tools for automating the theme development workflow:
- create_environment: Set up development environment for a customer theme
- get_screenshots: Capture UI screenshots for comparison with targets
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.types import Tool, TextContent
from pydantic import BaseModel, Field

# Configure logging - ONLY to file (not console) for stdio transport
log_file = Path("/tmp/mcp-server-debug.log")

try:
    # Clear previous log content
    with open(log_file, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("MCP Server Log Started\n")
        f.write("=" * 80 + "\n\n")

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(str(log_file), mode='a')  # ONLY file, no console
        ]
    )
    logger = logging.getLogger(__name__)
    logger.info(f"MCP Server logging to: {log_file}")
except Exception as e:
    # Fallback: no logging if file creation fails
    logging.basicConfig(level=logging.CRITICAL)
    logger = logging.getLogger(__name__)

# Initialize MCP server
app = Server("a12-theme-mcp")


# ============================================================================
# Tool Input/Output Schemas
# ============================================================================

class CreateEnvironmentInput(BaseModel):
    """Input schema for create_environment tool."""
    customer_name: str = Field(
        ...,
        description="Name of the customer/theme (alphanumeric only, no spaces)"
    )


class CreateEnvironmentOutput(BaseModel):
    """Output schema for create_environment tool."""
    success: bool
    theme_path: str
    screenshots_dir: str
    current_round: int
    frontend_url: str
    message: str


class GetScreenshotsInput(BaseModel):
    """Input schema for get_screenshots tool."""
    customer_name: str = Field(
        ...,
        description="Name of the customer/theme (must match existing environment)"
    )


class GetScreenshotsOutput(BaseModel):
    """Output schema for get_screenshots tool."""
    success: bool
    round_number: int
    screenshots: list[str]
    screenshots_dir: str
    message: str


# ============================================================================
# Tool Handlers
# ============================================================================

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="create_environment",
            description=(
                "Set up the development environment for a customer theme. "
                "This starts backend services, creates a theme file, "
                "prepares screenshot directory, and starts the frontend."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_name": {
                        "type": "string",
                        "description": "Name of the customer/theme (alphanumeric only)"
                    }
                },
                "required": ["customer_name"]
            }
        ),
        Tool(
            name="get_screenshots",
            description=(
                "Capture UI screenshots for the current theme iteration. "
                "This navigates through the UI workflow (login, theme selection, "
                "form creation, list view) and captures screenshots at each step."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_name": {
                        "type": "string",
                        "description": "Name of the customer/theme"
                    }
                },
                "required": ["customer_name"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls from MCP clients."""
    try:
        if name == "create_environment":
            # Import here to avoid circular dependencies
            sys.path.insert(0, str(Path(__file__).parent))
            from tools.create_environment import create_environment_handler

            input_data = CreateEnvironmentInput(**arguments)
            result = await create_environment_handler(input_data)

            return [TextContent(
                type="text",
                text=result.model_dump_json(indent=2)
            )]

        elif name == "get_screenshots":
            # Import here to avoid circular dependencies
            sys.path.insert(0, str(Path(__file__).parent))
            from tools.get_screenshots import get_screenshots_handler

            input_data = GetScreenshotsInput(**arguments)
            result = await get_screenshots_handler(input_data)

            return [TextContent(
                type="text",
                text=result.model_dump_json(indent=2)
            )]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        logger.error(f"Error handling tool {name}: {e}", exc_info=True)
        error_result = {
            "success": False,
            "message": f"Error: {str(e)}"
        }
        return [TextContent(
            type="text",
            text=str(error_result)
        )]


# ============================================================================
# Server Entry Point
# ============================================================================

async def main_stdio():
    """Run the MCP server on stdio transport."""
    logger.info("Starting A12 Theme MCP Server on stdio...")

    from mcp.server.stdio import stdio_server

    try:
        async with stdio_server() as (read_stream, write_stream):
            logger.info("MCP Server running on stdio")
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
    except Exception as e:
        logger.error(f"Error running server: {e}", exc_info=True)
        raise


async def main_sse(host: str = "localhost", port: int = 3000):
    """Run the MCP server on SSE (HTTP) transport."""
    logger.info(f"Starting A12 Theme MCP Server on SSE at {host}:{port}...")

    try:
        from mcp.server.sse import SseServerTransport
        from starlette.applications import Starlette
        from starlette.routing import Route
        from starlette.middleware import Middleware
        from starlette.middleware.cors import CORSMiddleware
        import uvicorn

        sse = SseServerTransport("/messages")

        async def handle_sse(request):
            async with sse.connect_sse(
                request.scope,
                request.receive,
                request._send,
            ) as streams:
                await app.run(
                    streams[0],
                    streams[1],
                    app.create_initialization_options(),
                )

        async def handle_messages(request):
            # The SSE transport handles the response internally
            # Don't return a Response object as it would cause double-send
            await sse.handle_post_message(
                request.scope,
                request.receive,
                request._send
            )

        # Create Starlette app with CORS middleware
        starlette_app = Starlette(
            routes=[
                Route("/sse", endpoint=handle_sse, methods=["GET"]),
                Route("/messages", endpoint=handle_messages, methods=["POST"]),
            ],
            middleware=[
                Middleware(
                    CORSMiddleware,
                    allow_origins=["*"],
                    allow_methods=["*"],
                    allow_headers=["*"],
                )
            ]
        )

        logger.info(f"MCP Server running on http://{host}:{port}")
        logger.info(f"SSE endpoint: http://{host}:{port}/sse")
        logger.info(f"Messages endpoint: http://{host}:{port}/messages")
        logger.info("CORS enabled for all origins")
        logger.info("Press Ctrl+C to stop")

        # Configure uvicorn with proper signal handling
        config = uvicorn.Config(
            starlette_app,
            host=host,
            port=port,
            log_level="info",
            # Enable graceful shutdown
            timeout_graceful_shutdown=2,
        )
        server = uvicorn.Server(config)

        # Set up signal handlers for clean shutdown
        import signal

        def signal_handler(sig, frame):
            logger.info("Shutting down server...")
            server.should_exit = True

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        await server.serve()

    except ImportError as e:
        logger.error(f"SSE transport requires additional dependencies: {e}")
        logger.error("Install with: pip install mcp[server] starlette uvicorn")
        raise
    except Exception as e:
        logger.error(f"Error running server: {e}", exc_info=True)
        raise


def run():
    """Entry point for running the server."""
    import argparse

    parser = argparse.ArgumentParser(description="A12 Theme MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="Transport type (default: stdio)"
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host for SSE transport (default: localhost)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=3000,
        help="Port for SSE transport (default: 3000)"
    )

    args = parser.parse_args()

    if args.transport == "stdio":
        asyncio.run(main_stdio())
    elif args.transport == "sse":
        asyncio.run(main_sse(args.host, args.port))


if __name__ == "__main__":
    run()
