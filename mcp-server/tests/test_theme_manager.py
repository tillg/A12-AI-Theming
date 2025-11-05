"""Tests for theme_manager service."""

import pytest
from pathlib import Path
import json
import tempfile
import shutil

from src.services.theme_manager import ThemeManager
from src.config.constants import THEMES_DIR, BASE_THEME_FILE


class TestThemeManager:
    """Test suite for ThemeManager."""

    def test_get_theme_path(self):
        """Test getting theme file path."""
        path = ThemeManager.get_theme_path("test-customer")
        assert isinstance(path, Path)
        assert path.name == "test-customer.json"
        assert path.parent == THEMES_DIR

    def test_theme_exists(self):
        """Test checking if theme exists."""
        # Default theme should exist
        assert ThemeManager.theme_exists("default")

        # Non-existent theme should not exist
        assert not ThemeManager.theme_exists("nonexistent-theme-xyz")

    def test_validate_theme_file(self):
        """Test theme file validation."""
        # Valid theme file (default.json should exist and be valid)
        if BASE_THEME_FILE.exists():
            assert ThemeManager.validate_theme_file(BASE_THEME_FILE)

        # Non-existent file should be invalid
        fake_path = Path("/nonexistent/path/theme.json")
        assert not ThemeManager.validate_theme_file(fake_path)

    def test_get_base_theme_content(self):
        """Test loading base theme content."""
        if BASE_THEME_FILE.exists():
            content = ThemeManager.get_base_theme_content()
            assert content is not None
            assert isinstance(content, dict)

    @pytest.mark.skip(reason="Requires write access to themes directory")
    def test_create_theme_file(self):
        """Test creating a new theme file.

        This test is skipped by default as it modifies the actual themes directory.
        Enable it for integration testing.
        """
        test_customer = "test-theme-pytest"

        try:
            # Create theme
            theme_path = ThemeManager.create_theme_file(test_customer)

            # Verify it was created
            assert theme_path.exists()
            assert ThemeManager.theme_exists(test_customer)
            assert ThemeManager.validate_theme_file(theme_path)

            # Verify content is valid JSON
            with open(theme_path, 'r') as f:
                content = json.load(f)
            assert isinstance(content, dict)

        finally:
            # Cleanup
            ThemeManager.delete_theme_file(test_customer)

    @pytest.mark.skip(reason="Requires write access to themes directory")
    def test_delete_theme_file(self):
        """Test deleting a theme file.

        This test is skipped by default as it modifies the actual themes directory.
        Enable it for integration testing.
        """
        test_customer = "test-theme-delete"

        # Create a theme
        theme_path = ThemeManager.create_theme_file(test_customer)
        assert theme_path.exists()

        # Delete it
        result = ThemeManager.delete_theme_file(test_customer)
        assert result is True
        assert not theme_path.exists()

        # Delete non-existent theme
        result = ThemeManager.delete_theme_file(test_customer)
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
