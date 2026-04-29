#!/bin/bash
set -e

# Forward SIGTERM/SIGINT to the children so `docker stop` exits cleanly
# instead of waiting for the stop timeout.
shutdown() {
	kill -TERM "$UVICORN_PID" "$NGINX_PID" 2>/dev/null || true
	wait "$UVICORN_PID" "$NGINX_PID" 2>/dev/null || true
}
trap shutdown SIGTERM SIGINT

uvicorn app.main:app \
	--host 127.0.0.1 \
	--port 8000 \
	--workers 1 \
	--log-level warning &
UVICORN_PID=$!

nginx -g "daemon off;" &
NGINX_PID=$!

# Exit as soon as either process dies, then make sure the other one is
# torn down before the container exits so we don't leak orphans.
wait -n
EXIT_CODE=$?
shutdown
exit "$EXIT_CODE"
