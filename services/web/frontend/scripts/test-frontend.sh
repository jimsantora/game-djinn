#!/bin/bash
# Frontend testing script with automatic timeout

echo "Starting frontend development server test..."

# Start the dev server in background
npm run dev &
DEV_PID=$!

# Wait for server to start
echo "Waiting for server to start..."
sleep 5

# Check if server is running
if curl -s http://localhost:3001 > /dev/null 2>&1; then
    echo "✓ Frontend server started successfully on port 3001"
    echo "✓ Server responding to requests"
elif curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "✓ Frontend server started successfully on port 3000"
    echo "✓ Server responding to requests"
else
    echo "✗ Frontend server failed to start or not responding"
fi

# Keep server running for 25 more seconds for manual testing
echo "Server will run for 25 more seconds for testing..."
sleep 25

# Stop the server
echo "Stopping development server..."
kill $DEV_PID 2>/dev/null || true

# Wait for cleanup
sleep 2

# Check if any vite processes are still running
if pgrep -f vite > /dev/null; then
    echo "Force killing remaining vite processes..."
    pkill -f vite
fi

echo "✓ Frontend test complete"