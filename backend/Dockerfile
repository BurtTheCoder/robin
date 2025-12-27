FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Robin agent code (parent directory)
COPY ../agent /app/agent
COPY ../core /app/core
COPY ../config.py /app/config.py

# Copy backend code
COPY app /app/backend/app

# Set Python path
ENV PYTHONPATH=/app:/app/backend

# Expose port
EXPOSE 8000

# Run server
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
