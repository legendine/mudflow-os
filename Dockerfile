# Production Dockerfile for MudFlow OS v2.5
FROM python:3.10-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set container working directory
WORKDIR /app

# Copy dependency requirements first to optimize Docker layer cache
COPY requirements.txt /app/requirements.txt

# Install locked dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application source code and assets
COPY . /app/

# Ensure persistent storage directories exist
RUN mkdir -p /app/data /app/data/reports_pdf

# Expose MudFlow OS service port
EXPOSE 9001

# Start production server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9001"]
