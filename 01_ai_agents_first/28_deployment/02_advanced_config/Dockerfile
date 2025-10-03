FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create and switch to non-root user
RUN useradd -m -u 1000 user
USER user

# Set up environment
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PORT=7860 \
    CHAINLIT_HOST=0.0.0.0 \
    PYTHONUNBUFFERED=1

WORKDIR $HOME/app

# Copy application files with correct ownership
COPY --chown=user:user . .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port
EXPOSE 7860

# Run the application
CMD ["chainlit", "run", "app.py", "--port", "7860"] 