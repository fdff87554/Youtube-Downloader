#!/bin/sh
set -e

# Start uvicorn in background
uvicorn app.main:app \
	--host 127.0.0.1 \
	--port 8000 \
	--workers 1 \
	--log-level warning &

# Start nginx in foreground
nginx -g "daemon off;"
