#!/bin/bash
# API testing script with server management

# Set environment variables
export DATABASE_URL="postgresql://gamedjinn:secure-password-here@localhost:5432/gamedjinn"
export REDIS_URL="redis://localhost:6379"
export SECRET_KEY="dev-secret-key-change-in-production"
export MCP_API_KEY="dev-mcp-key"

echo "Starting API test sequence..."

# Check if server is running
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✓ Server is already running"
else
    echo "Starting development server..."
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
    SERVER_PID=$!
    
    # Wait for server to start
    echo "Waiting for server to start..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo "✓ Server started successfully"
            break
        fi
        sleep 1
    done
    
    if [ $i -eq 30 ]; then
        echo "✗ Server failed to start"
        exit 1
    fi
fi

# Run API tests
echo "Running API tests..."
python scripts/test_api.py

# If we started the server, stop it
if [ ! -z "$SERVER_PID" ]; then
    echo "Stopping development server..."
    kill $SERVER_PID 2>/dev/null || true
fi

echo "API test sequence complete"