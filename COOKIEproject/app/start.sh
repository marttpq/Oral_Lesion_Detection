#!/bin/sh
# start.sh — Download missing assets, then run Redis + RQ worker + Gunicorn
# Optimised for 1-2 vCPU / 2 GB RAM (Railway free/starter tier).

set -e

# ── 1. Download static assets bundle if not already present ─────────────────
if [ ! -f "static/image/img2.png" ]; then
    if [ -n "$ASSETS_DOWNLOAD_URL" ]; then
        echo "[start.sh] Downloading static assets from ASSETS_DOWNLOAD_URL..."
        curl -fsSL "$ASSETS_DOWNLOAD_URL" -o /tmp/assets.zip
        unzip -o /tmp/assets.zip -d /app/
        rm -f /tmp/assets.zip
        echo "[start.sh] Static assets extracted."
    else
        echo "[start.sh] WARNING: static/image/img2.png not found and ASSETS_DOWNLOAD_URL not set."
        echo "[start.sh] Images will be missing. Set ASSETS_DOWNLOAD_URL in Railway variables."
    fi
fi

# ── 2. Start Redis (only if no external REDIS_URL is set) ────────────────────
if [ -z "$REDIS_URL" ]; then
    echo "[start.sh] No REDIS_URL set — starting bundled Redis on port 6379..."
    redis-server --daemonize yes --loglevel warning
    export REDIS_URL="redis://localhost:6379/0"
    # Give Redis a moment to come up before RQ tries to connect
    sleep 1
else
    echo "[start.sh] Using external Redis: $REDIS_URL"
fi

# ── 3. Start RQ worker in background ────────────────────────────────────────
echo "[start.sh] Starting custom RQ worker (worker.py) for inference-tasks..."
python worker.py &
RQ_PID=$!
echo "[start.sh] RQ worker started (PID $RQ_PID)."

# ── 4. Start Gunicorn with gevent worker ────────────────────────────────────
# gevent: single OS process, N greenlet connections — ideal for low-RAM VMs.
#   --workers 1          : one OS worker process (low RAM, avoids model duplication)
#   --worker-class gevent: async I/O via greenlets (handles many concurrent requests)
#   --worker-connections 8: up to 8 concurrent connections per worker
#   --timeout 180        : allow slow inference to complete (YOLOv7 ~5 s on CPU)
#   --keep-alive 5       : reuse HTTP connections for a few seconds
echo "[start.sh] Starting Gunicorn (gevent) on port ${PORT:-8080}..."
exec gunicorn \
    --workers 1 \
    --worker-class gevent \
    --worker-connections 8 \
    --timeout 180 \
    --keep-alive 5 \
    --bind "0.0.0.0:${PORT:-8080}" \
    --access-logfile - \
    --error-logfile - \
    app1:app
