# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
# Copy requirements.txt before installing dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Debug: List contents of /app to verify app/ is present
RUN ls -l /app

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY . .
RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir -p uploads models data/synthetic archives

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser
# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

RUN echo '--- /app contents ---' && ls -l /app && echo '--- /app/app contents ---' && ls -l /app/app || true

# Set PYTHONPATH so 'app' is importable
ENV PYTHONPATH=/app
# Start the application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]