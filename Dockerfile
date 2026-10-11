# ==============================================================================
# AI Plant Care — Production Containerfile
# Hardened multi-stage/lean image with non-root execution and healthcheck
# ==============================================================================

FROM python:3.11-slim

WORKDIR /app

# Python runtime environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_ENV=production \
    PORT=5000

# Install essential system dependencies for OpenCV, healthcheck, and SSL
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies first for efficient Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Ensure uploads directory exists and compile translation catalogs
RUN mkdir -p uploads && \
    python -m babel.messages.frontend compile -d app/translations

# Create non-root user for security hardening
RUN useradd -u 1000 -m appuser && \
    chown -R appuser:appuser /app

USER appuser

# Expose internal web port
EXPOSE 5000

# Container healthcheck against /health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Start WSGI production server with Gunicorn (reads gunicorn.conf.py)
CMD ["gunicorn", "-c", "gunicorn.conf.py", "run:app"]
