# Stage 1: Build frontend
FROM node:22-alpine AS frontend-build
WORKDIR /build
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# Stage 2: Install backend dependencies
FROM python:3.12-slim AS backend-deps
WORKDIR /build
RUN pip install --no-cache-dir --upgrade pip
COPY backend/pyproject.toml .
RUN pip install --no-cache-dir --prefix=/install .

# Stage 3: Runtime
FROM python:3.12-slim

# Install nginx and ffmpeg (required for yt-dlp audio/video muxing)
RUN apt-get update \
    && apt-get install -y --no-install-recommends nginx ffmpeg curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies
COPY --from=backend-deps /install /usr/local

# Copy backend source
WORKDIR /app
COPY backend/app/ ./app/

# Copy built frontend
COPY --from=frontend-build /build/dist /var/www/html

# Copy nginx config
COPY docker/nginx.conf /etc/nginx/nginx.conf

# Copy entrypoint
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8080

ENTRYPOINT ["/entrypoint.sh"]
