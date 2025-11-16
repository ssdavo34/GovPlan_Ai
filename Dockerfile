# Multi-stage build for production
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    curl \
    wget \
    chromium \
    chromium-driver \
    fonts-nanum \
    fonts-nanum-coding \
    && rm -rf /var/lib/apt/lists/*

# Development stage
FROM base as development

# Install Python dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Install development tools
RUN pip install --no-cache-dir \
    pytest \
    pytest-asyncio \
    pytest-cov \
    black \
    flake8 \
    mypy

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/uploads /app/documents /app/logs

# Expose port
EXPOSE 8000

# Default command
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM base as production

# Install Python dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy only necessary files
COPY backend ./backend
COPY scripts ./scripts
COPY database ./database
COPY config ./config
COPY .env.example .env.example

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/uploads /app/documents /app/logs && \
    chown -R appuser:appuser /app

USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
