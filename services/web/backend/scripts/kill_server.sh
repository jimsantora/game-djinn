#!/bin/bash
# Clean server shutdown script

echo "Stopping all uvicorn processes..."

# Kill any running uvicorn processes
pkill -f uvicorn

# Wait for cleanup
sleep 2

# Check if any processes are still running
if pgrep -f uvicorn > /dev/null; then
    echo "Force killing remaining uvicorn processes..."
    pkill -9 -f uvicorn
    sleep 1
fi

if pgrep -f uvicorn > /dev/null; then
    echo "✗ Some uvicorn processes may still be running"
    echo "Active uvicorn processes:"
    pgrep -af uvicorn
else
    echo "✓ All uvicorn processes stopped"
fi