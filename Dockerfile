FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (no poetry to avoid FastAPI detection)
COPY requirements.txt ./

# Install dependencies directly with pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Use a simple server.py script to completely bypass detection
CMD ["python", "server.py"]
