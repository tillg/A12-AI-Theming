"""Theme management service for creating and validating theme files.

This module handles theme file operations:
- Creating new theme files from templates
- Validating theme JSON structure
- Managing theme file paths
"""

import json
import logging
import shutil
from pathlib import Path
from typing import Optional

from config.constants import (
    THEMES_DIR,
    BASE_THEME_FILE,
)

logger = logging.getLogger(__name__)


class ThemeManager:
    """Manages theme file operations."""

    @staticmethod
    def create_theme_file(customer_name: str) -> Path:
        """Create a new theme file for a customer by copying the base template.

        Args:
            customer_name: Name of the customer/theme

        Returns:
            Path: Path to the created theme file

        Raises:
            FileNotFoundError: If base theme template doesn't exist
            IOError: If theme file creation fails
        """
        logger.info(f"Creating theme file for customer: {customer_name}")

        # Ensure themes directory exists
        THEMES_DIR.mkdir(parents=True, exist_ok=True)

        # Define target theme file path
        theme_path = THEMES_DIR / f"{customer_name}.json"

        # Check if theme already exists
        if theme_path.exists():
            logger.warning(f"Theme file already exists: {theme_path}")
            return theme_path

        # Check if base theme exists
        if not BASE_THEME_FILE.exists():
            logger.error(f"Base theme template not found: {BASE_THEME_FILE}")
            raise FileNotFoundError(f"Base theme template not found: {BASE_THEME_FILE}")

        try:
            # Copy base theme to new customer theme
            shutil.copy2(BASE_THEME_FILE, theme_path)
            logger.info(f"Theme file created: {theme_path}")

            # Validate the created file
            if not ThemeManager.validate_theme_file(theme_path):
                logger.error(f"Created theme file is invalid: {theme_path}")
                theme_path.unlink()  # Delete invalid file
                raise ValueError(f"Created theme file is invalid: {theme_path}")

            return theme_path

        except Exception as e:
            logger.error(f"Error creating theme file: {e}", exc_info=True)
            raise IOError(f"Failed to create theme file: {e}")

    @staticmethod
    def validate_theme_file(theme_path: Path) -> bool:
        """Validate that a theme file has valid JSON structure.

        Args:
            theme_path: Path to the theme file

        Returns:
            bool: True if valid, False otherwise
        """
        try:
            if not theme_path.exists():
                logger.error(f"Theme file does not exist: {theme_path}")
                return False

            # Try to load and parse JSON
            with open(theme_path, 'r', encoding='utf-8') as f:
                theme_data = json.load(f)

            # Basic validation: should be a dict/object
            if not isinstance(theme_data, dict):
                logger.error(f"Theme file is not a JSON object: {theme_path}")
                return False

            logger.debug(f"Theme file is valid: {theme_path}")
            return True

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in theme file {theme_path}: {e}")
            return False

        except Exception as e:
            logger.error(f"Error validating theme file {theme_path}: {e}", exc_info=True)
            return False

    @staticmethod
    def get_theme_path(customer_name: str) -> Path:
        """Get the path to a customer's theme file.

        Args:
            customer_name: Name of the customer/theme

        Returns:
            Path: Path to the theme file (may not exist yet)
        """
        return THEMES_DIR / f"{customer_name}.json"

    @staticmethod
    def theme_exists(customer_name: str) -> bool:
        """Check if a theme file exists for a customer.

        Args:
            customer_name: Name of the customer/theme

        Returns:
            bool: True if theme file exists, False otherwise
        """
        theme_path = ThemeManager.get_theme_path(customer_name)
        return theme_path.exists()

    @staticmethod
    def delete_theme_file(customer_name: str) -> bool:
        """Delete a customer's theme file.

        Args:
            customer_name: Name of the customer/theme

        Returns:
            bool: True if deleted, False if file didn't exist
        """
        theme_path = ThemeManager.get_theme_path(customer_name)

        if not theme_path.exists():
            logger.warning(f"Theme file does not exist: {theme_path}")
            return False

        try:
            theme_path.unlink()
            logger.info(f"Theme file deleted: {theme_path}")
            return True

        except Exception as e:
            logger.error(f"Error deleting theme file {theme_path}: {e}", exc_info=True)
            return False

    @staticmethod
    def get_base_theme_content() -> Optional[dict]:
        """Load and return the base theme template content.

        Returns:
            dict: Base theme data, or None if error
        """
        try:
            if not BASE_THEME_FILE.exists():
                logger.error(f"Base theme file does not exist: {BASE_THEME_FILE}")
                return None

            with open(BASE_THEME_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)

        except Exception as e:
            logger.error(f"Error loading base theme: {e}", exc_info=True)
            return None
