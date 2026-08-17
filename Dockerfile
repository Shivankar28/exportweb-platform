FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose Flask default port
EXPOSE 5000

# Run seed script and launch Gunicorn
CMD ["sh", "-c", "python seed.py && gunicorn wsgi:app --bind 0.0.0.0:5000 --workers 4"]
