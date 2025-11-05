"""Process management service for backend and frontend services.

This module handles starting, stopping, and health checking of:
- Backend services (Gradle + Docker Compose)
- Frontend development server (npm)
"""

import asyncio
import atexit
import logging
import signal
import sys
from pathlib import Path
from typing import Optional
import aiohttp

from config.constants import (
    PROJECT_ROOT,
    CLIENT_DIR,
    BACKEND_URL,
    FRONTEND_URL,
    BACKEND_STARTUP_TIMEOUT,
    FRONTEND_STARTUP_TIMEOUT,
    HEALTH_CHECK_INTERVAL,
    GRADLE_BACKEND_CMD,
    NPM_START_CMD,
)

logger = logging.getLogger(__name__)


class ProcessManager:
    """Manages lifecycle of backend and frontend processes."""

    # Class-level process tracking to prevent duplicates
    _backend_process: Optional[asyncio.subprocess.Process] = None
    _frontend_process: Optional[asyncio.subprocess.Process] = None
    _is_shutting_down: bool = False

    @classmethod
    def _setup_signal_handlers(cls):
        """Set up signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating shutdown...")
            cls._is_shutting_down = True
            asyncio.create_task(cls.cleanup_all())
            sys.exit(0)

        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Register atexit handler
        atexit.register(lambda: asyncio.run(cls.cleanup_all()))

    @classmethod
    async def start_backend(cls) -> bool:
        """Start backend services using Gradle.

        Returns:
            bool: True if started successfully, False otherwise
        """
        if cls._backend_process is not None:
            logger.info("Backend process already running")
            return True

        logger.info("Starting backend services...")

        try:
            # Start the gradle process
            cls._backend_process = await asyncio.create_subprocess_exec(
                *GRADLE_BACKEND_CMD,
                cwd=str(PROJECT_ROOT),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            logger.info(f"Backend process started with PID {cls._backend_process.pid}")

            # Wait for backend to be healthy
            if await cls._wait_for_health(BACKEND_URL, BACKEND_STARTUP_TIMEOUT):
                logger.info("Backend services are healthy")
                return True
            else:
                logger.error("Backend services failed health check")
                await cls.stop_backend()
                return False

        except Exception as e:
            logger.error(f"Error starting backend: {e}", exc_info=True)
            await cls.stop_backend()
            return False

    @classmethod
    async def start_frontend(cls) -> bool:
        """Start frontend development server using npm.

        Returns:
            bool: True if started successfully, False otherwise
        """
        if cls._frontend_process is not None:
            logger.info("Frontend process already running")
            return True

        logger.info("Starting frontend development server...")

        try:
            # Start npm in the client directory
            cls._frontend_process = await asyncio.create_subprocess_exec(
                *NPM_START_CMD,
                cwd=str(CLIENT_DIR),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            logger.info(f"Frontend process started with PID {cls._frontend_process.pid}")

            # Wait for frontend to be healthy
            if await cls._wait_for_health(FRONTEND_URL, FRONTEND_STARTUP_TIMEOUT):
                logger.info("Frontend development server is healthy")
                return True
            else:
                logger.error("Frontend development server failed health check")
                await cls.stop_frontend()
                return False

        except Exception as e:
            logger.error(f"Error starting frontend: {e}", exc_info=True)
            await cls.stop_frontend()
            return False

    @classmethod
    async def stop_backend(cls):
        """Stop backend services gracefully."""
        if cls._backend_process is None:
            logger.info("No backend process to stop")
            return

        logger.info("Stopping backend services...")

        try:
            # Try graceful termination first
            cls._backend_process.terminate()

            # Wait up to 10 seconds for graceful shutdown
            try:
                await asyncio.wait_for(cls._backend_process.wait(), timeout=10.0)
                logger.info("Backend services stopped gracefully")
            except asyncio.TimeoutError:
                # Force kill if not stopped
                logger.warning("Backend did not stop gracefully, forcing kill...")
                cls._backend_process.kill()
                await cls._backend_process.wait()
                logger.info("Backend services killed")

        except Exception as e:
            logger.error(f"Error stopping backend: {e}", exc_info=True)

        finally:
            cls._backend_process = None

    @classmethod
    async def stop_frontend(cls):
        """Stop frontend development server."""
        if cls._frontend_process is None:
            logger.info("No frontend process to stop")
            return

        logger.info("Stopping frontend development server...")

        try:
            # Try graceful termination first
            cls._frontend_process.terminate()

            # Wait up to 5 seconds for graceful shutdown
            try:
                await asyncio.wait_for(cls._frontend_process.wait(), timeout=5.0)
                logger.info("Frontend stopped gracefully")
            except asyncio.TimeoutError:
                # Force kill if not stopped
                logger.warning("Frontend did not stop gracefully, forcing kill...")
                cls._frontend_process.kill()
                await cls._frontend_process.wait()
                logger.info("Frontend killed")

        except Exception as e:
            logger.error(f"Error stopping frontend: {e}", exc_info=True)

        finally:
            cls._frontend_process = None

    @classmethod
    async def cleanup_all(cls):
        """Clean up all running processes."""
        if cls._is_shutting_down:
            return

        cls._is_shutting_down = True
        logger.info("Cleaning up all processes...")

        await cls.stop_frontend()
        await cls.stop_backend()

        logger.info("All processes cleaned up")

    @classmethod
    async def is_backend_healthy(cls) -> bool:
        """Check if backend services are responding.

        Returns:
            bool: True if healthy, False otherwise
        """
        return await cls._check_health(BACKEND_URL)

    @classmethod
    async def is_frontend_healthy(cls) -> bool:
        """Check if frontend is responding.

        Returns:
            bool: True if healthy, False otherwise
        """
        return await cls._check_health(FRONTEND_URL)

    @classmethod
    async def is_environment_running(cls) -> bool:
        """Check if both backend and frontend are running.

        Returns:
            bool: True if both are healthy, False otherwise
        """
        # Check if services are responding (regardless of how they were started)
        backend_healthy = await cls.is_backend_healthy()
        frontend_healthy = await cls.is_frontend_healthy()

        logger.info(f"Environment health check: backend={backend_healthy}, frontend={frontend_healthy}")

        return backend_healthy and frontend_healthy

    @classmethod
    async def _check_health(cls, url: str, timeout: float = 5.0) -> bool:
        """Check if a service is responding to HTTP requests.

        Args:
            url: URL to check
            timeout: Request timeout in seconds

        Returns:
            bool: True if service responds (including 404), False on connection error
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(total=timeout),
                    allow_redirects=True
                ) as response:
                    # Accept any response including 404 - we just want to know the server is running
                    # 404 is normal for Spring Boot apps without a root endpoint
                    return 200 <= response.status < 500

        except Exception as e:
            logger.debug(f"Health check failed for {url}: {e}")
            return False

    @classmethod
    async def _wait_for_health(
        cls,
        url: str,
        timeout: float,
        check_interval: float = HEALTH_CHECK_INTERVAL
    ) -> bool:
        """Wait for a service to become healthy.

        Args:
            url: URL to check
            timeout: Maximum time to wait in seconds
            check_interval: Time between checks in seconds

        Returns:
            bool: True if service became healthy, False if timeout
        """
        logger.info(f"Waiting for {url} to become healthy (timeout: {timeout}s)...")

        elapsed = 0.0
        while elapsed < timeout:
            if await cls._check_health(url):
                return True

            await asyncio.sleep(check_interval)
            elapsed += check_interval
            logger.debug(f"Still waiting for {url}... ({elapsed:.0f}s elapsed)")

        logger.error(f"Timeout waiting for {url} to become healthy")
        return False


# Set up signal handlers when module is imported
ProcessManager._setup_signal_handlers()
