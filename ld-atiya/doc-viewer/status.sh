#!/bin/bash
# Check documentation viewer status

cd /home/test/reg/agent-dp/ld-atiya/doc-viewer

echo "=== Documentation Viewer Status ==="
echo ""

if [ -f server.pid ]; then
    PID=$(cat server.pid)
    if kill -0 $PID 2>/dev/null; then
        echo "✓ Server is RUNNING"
        echo "  PID: $PID"
        echo ""
        echo "Access URLs:"
        echo "  Local:    http://127.0.0.1:5000"
        echo "  Network:  http://10.2.182.163:5000"
        echo "  Internal: http://192.168.100.5:5000"
        echo ""
        echo "Recent logs:"
        tail -5 server.log
    else
        echo "✗ Server is STOPPED (stale PID file)"
        rm server.pid
    fi
else
    echo "✗ Server is STOPPED"
fi
