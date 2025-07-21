#!/bin/bash
# Development server startup script

# Set environment variables
export DATABASE_URL="postgresql://gamedjinn:secure-password-here@localhost:5432/gamedjinn"
export REDIS_URL="redis://localhost:6379"
export SECRET_KEY="dev-secret-key-change-in-production"
export MCP_API_KEY="dev-mcp-key"

# Kill any existing uvicorn processes
pkill -f uvicorn 2>/dev/null || true

# Wait a moment for cleanup
sleep 2

# Start the development server
echo "Starting Game Djinn Web API on http://localhost:8000"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000