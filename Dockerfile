FROM python:3.13-alpine

# Set working directory
WORKDIR /app

# Install uv for faster dependency management
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN uv sync --frozen --no-dev

# Copy application code
COPY server.py config.py cache_manager.py ./

# Copy README if needed for documentation
COPY README.md ./

# Create a non-root user for security
RUN adduser -D -s /bin/sh app && \
    chown -R app:app /app

# Create a writable cache directory for uv
RUN mkdir -p /tmp/uv-cache && \
    chown -R app:app /tmp/uv-cache

USER app

# Expose port for HTTP mode (optional)
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV UV_CACHE_DIR=/tmp/uv-cache

# Default command runs the MCP server in stdio mode
CMD ["uv", "run", "python", "server.py"]
