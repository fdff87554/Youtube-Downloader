#!/bin/bash
set -e

# Start uvicorn in background
uvicorn app.main:app \
	--host 127.0.0.1 \
	--port 8000 \
	--workers 1 \
	--log-level warning &

# Start nginx in background
nginx -g "daemon off;" &

# Exit container if either process dies
wait -n
exit 1
