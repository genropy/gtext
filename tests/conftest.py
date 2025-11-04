"""Pytest configuration and fixtures."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from gtext.config import Config


@pytest.fixture(autouse=True)
def setup_permissive_security(request):
    """Setup permissive security rules for all tests.

    This fixture allows existing tests to work with the new security system
    by configuring permissive rules. Security-specific tests are automatically
    excluded based on test module name.
    """
    # Skip this fixture for security-specific test modules
    security_test_modules = [
        "test_cli_security",
        "test_security_integration",
        "test_config",
    ]

    test_module = request.node.module.__name__
    if any(module in test_module for module in security_test_modules):
        # Don't set up permissive rules for security tests
        yield None
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, "home", return_value=Path(tmpdir)):
            config = Config()
            # Allow all CLI commands (for testing)
            config.add_rule("cli", "*", "allow", use_global=True)
            # Allow all static file includes (for testing)
            config.add_rule("static", "*", "allow", use_global=True)
            # Allow all glob patterns (for testing)
            config.add_rule("glob", "*", "allow", use_global=True)

            yield config
