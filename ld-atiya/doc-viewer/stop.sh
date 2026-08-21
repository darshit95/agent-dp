#!/bin/bash
# Stop the documentation viewer

cd /home/test/reg/agent-dp/ld-atiya/doc-viewer

if [ -f server.pid ]; then
    PID=$(cat server.pid)
    if kill -0 $PID 2>/dev/null; then
        echo "Stopping server (PID: $PID)..."
        kill $PID
        sleep 1

        # Force kill if still running
        if kill -0 $PID 2>/dev/null; then
            echo "Force stopping server..."
            kill -9 $PID
        fi

        rm server.pid
        echo "Server stopped successfully"
    else
        echo "Server is not running (PID $PID not found)"
        rm server.pid
    fi
else
    echo "No PID file found. Checking for running Flask processes..."
    pkill -f "python app.py" && echo "Stopped Flask processes" || echo "No Flask processes found"
fi
