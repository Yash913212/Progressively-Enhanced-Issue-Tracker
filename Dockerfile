FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System dependencies (psycopg2 needs libpq, libpq-dev for compilation fallback)
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Ensure the entrypoint script is executable
RUN chmod +x /app/entrypoint.sh

# Create a non-root user to run the application
RUN adduser --disabled-password --gecos "" appuser \
    && mkdir -p /app/staticfiles \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
