# Use multi-stage build for smaller final image
FROM python:3.9-slim as builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Second stage: Runtime
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Create non-root user
RUN useradd -m -u 1000 user \
    && chown -R user:user /app

# Copy Python dependencies from builder
COPY --from=builder /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=7860

# Copy application files
COPY . .

# Switch to non-root user
USER user

# Expose port for Hugging Face Spaces
EXPOSE 7860

# Command to run the application
CMD ["chainlit", "run", "main.py", "--host", "0.0.0.0", "--port", "7860"] 