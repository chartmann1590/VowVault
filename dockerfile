FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies including ffmpeg
RUN apt-get update && apt-get install -y \
    gcc \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY migration.py .
COPY templates/ templates/
COPY static/ static/

# Create upload directories
RUN mkdir -p static/uploads static/uploads/guestbook static/uploads/messages static/uploads/videos static/uploads/thumbnails

# Make migration script executable
RUN chmod +x migration.py

# Set environment variables
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1

# Create entrypoint script
RUN echo '#!/bin/sh\n\
echo "Running database migrations..."\n\
python migration.py\n\
echo "Starting Flask application..."\n\
python app.py' > /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

# Expose port
EXPOSE 5000

# Run migrations and then the application
ENTRYPOINT ["/app/entrypoint.sh"]