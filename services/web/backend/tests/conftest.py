"""Test configuration and fixtures."""

import pytest
import os
from unittest.mock import patch

# Set environment variables for testing
test_env = {
    "DATABASE_URL": "sqlite+aiosqlite:///:memory:",
    "SECRET_KEY": "test-secret-key",
    "MCP_API_KEY": "test-mcp-key",
    "ADMIN_EMAIL": "",
    "ADMIN_PASSWORD": "",
}


@pytest.fixture(scope="session", autouse=True)
def set_test_env():
    """Set test environment variables."""
    with patch.dict(os.environ, test_env):
        yield