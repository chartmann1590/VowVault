FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies including ffmpeg
RUN apt-get update && apt-get install -y \
    gcc \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app/ app/
COPY run.py .
COPY migration.py .
COPY docker-entrypoint.sh .
COPY templates/ templates/
COPY static/ static/

# Create upload directories
RUN mkdir -p static/uploads static/uploads/guestbook static/uploads/messages static/uploads/videos static/uploads/thumbnails static/uploads/photobooth static/uploads/borders

# Make scripts executable
RUN chmod +x migration.py docker-entrypoint.sh

# Set environment variables
ENV FLASK_APP=run.py
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 5000

# Use the new entrypoint script
ENTRYPOINT ["/app/docker-entrypoint.sh"]