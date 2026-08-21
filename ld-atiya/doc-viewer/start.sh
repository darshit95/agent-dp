#!/bin/bash
# Start the documentation viewer

cd /home/test/reg/agent-dp/ld-atiya/doc-viewer

# Check if already running
if [ -f server.pid ]; then
    PID=$(cat server.pid)
    if kill -0 $PID 2>/dev/null; then
        echo "Server is already running (PID: $PID)"
        echo "Use ./stop.sh to stop it first"
        exit 1
    else
        rm server.pid
    fi
fi

# Start server in background
nohup /home/test/reg/bin/python app.py > server.log 2>&1 & echo $! > server.pid

sleep 2
PID=$(cat server.pid)

if kill -0 $PID 2>/dev/null; then
    echo "Server started successfully!"
    echo "PID: $PID"
    echo "URL: http://127.0.0.1:5000"
    echo "Logs: $(pwd)/server.log"
    echo ""
    echo "Use ./stop.sh to stop the server"
else
    echo "Failed to start server. Check server.log for details"
    exit 1
fi
