"""Simplified HTTP/SSE MCP Server for A12 Theme Development.

This is a simpler implementation that uses basic SSE without the MCP SSE transport wrapper.
Use this if the main server.py has compatibility issues with the Inspector.
"""

import asyncio
import json
import logging
from typing import Any
from starlette.applications import Starlette
from starlette.responses import StreamingResponse, JSONResponse
from starlette.routing import Route
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
import uvicorn

# Import from main server
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from server import app, logger

# Active SSE connections
connections = {}


async def handle_sse(request):
    """Handle SSE connection from client."""
    session_id = request.query_params.get('session_id', 'default')

    async def event_generator():
        # Keep connection alive
        while True:
            # Send a comment to keep connection alive
            yield f": keepalive\n\n"
            await asyncio.sleep(15)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


async def handle_messages(request):
    """Handle JSON-RPC messages from client."""
    try:
        body = await request.json()
        logger.info(f"Received message: {body}")

        # For now, just echo back
        response = {
            "jsonrpc": "2.0",
            "id": body.get("id"),
            "result": {"message": "Message received"}
        }

        return JSONResponse(response)

    except Exception as e:
        logger.error(f"Error handling message: {e}", exc_info=True)
        return JSONResponse(
            {"error": str(e)},
            status_code=500
        )


# Create Starlette app
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


def run(host: str = "localhost", port: int = 3001):
    """Run the simple HTTP server."""
    logger.info(f"Starting Simple HTTP MCP Server at {host}:{port}...")
    logger.info(f"SSE endpoint: http://{host}:{port}/sse")
    logger.info(f"Messages endpoint: http://{host}:{port}/messages")

    config = uvicorn.Config(starlette_app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)
    asyncio.run(server.serve())


if __name__ == "__main__":
    run()
