# MCP Server Tests

## Overview

This directory contains the test suite for the Game Djinn MCP Server tools. The tests ensure that all MCP tools work correctly with proper database integration and error handling.

## Test Structure

- `conftest.py` - Test configuration and fixtures (in-memory database, session management)
- `test_platforms.py` - Tests for platform management tools
- `test_games.py` - Tests for game search and details tools
- `test_recommendations.py` - Tests for game recommendation tool

## Running Tests

### Using the Makefile (Recommended)

From the project root directory:

```bash
# Run all MCP tests
make test-mcp

# Run tests locally (requires local Python environment)
make test-mcp-local

# Run specific tool tests (pattern matching)
make test-mcp-tools PATTERN=search
make test-mcp-tools PATTERN=recommend

# Install test dependencies locally
make test-mcp-install
```

### Direct pytest commands

From the `services/mcp-server` directory:

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_games.py -v

# Run tests matching a pattern
pytest tests/ -k "search" -v

# Run with minimal output
pytest tests/ -q
```

## Test Database

Tests use an in-memory SQLite database that is created fresh for each test function. This ensures:
- Tests are isolated from each other
- No persistent data between test runs
- Fast test execution
- No need for external database setup

## Writing New Tests

1. Create a new test file following the pattern `test_<tool_name>.py`
2. Import the necessary fixtures from `conftest.py`
3. Use the `override_get_session` fixture to ensure tools use the test database
4. Follow the existing test patterns for consistency

Example test structure:

```python
import pytest
from tools.your_tool import your_function

@pytest.mark.asyncio
async def test_your_function(test_session, override_get_session):
    """Test description."""
    # Setup test data
    # Call the tool function
    result = await your_function(param1="value1")
    
    # Assert expected results
    assert "expected_key" in result
    assert result["expected_key"] == "expected_value"
```

## Test Coverage

Current test coverage includes:
- Platform management (listing, adding libraries)
- Game search (with filters)
- Game details (with and without user data)
- Recommendations (with user preferences and criteria)
- Error handling for edge cases

## Continuous Integration

These tests are designed to run in CI/CD pipelines and can be integrated with GitHub Actions or other CI systems.