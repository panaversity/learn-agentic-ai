# Dockerfile Best Practices for Python Applications

## Objective
This guide provides best practices for creating efficient, secure, and maintainable Dockerfiles for Python applications, specifically optimized for Azure Container Apps deployment.

## Prerequisites
- Docker installed locally
- Basic understanding of Docker concepts
- Python application codebase
- UV package manager installed

## Step-by-Step Instructions

### 1. Create Base Dockerfile

```dockerfile
# Use Python slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install UV
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies using UV
RUN uv pip install --system

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Set entrypoint
ENTRYPOINT ["python", "-m", "your_application"]
```

### 2. Multi-stage Build for Production

```dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install UV
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN uv pip install --system

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Copy only necessary files from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Set entrypoint
ENTRYPOINT ["python", "-m", "your_application"]
```

### 3. Development Dockerfile

```dockerfile
# Development stage
FROM python:3.11-slim

WORKDIR /app

# Install development dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install UV
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN uv pip install --system

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Set entrypoint
ENTRYPOINT ["uvicorn", "your_application.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

## Best Practices

### 1. Security
- Use non-root user
- Keep base images updated
- Scan for vulnerabilities
- Use multi-stage builds
- Remove unnecessary tools

### 2. Performance
- Leverage layer caching
- Minimize layers
- Use .dockerignore
- Optimize dependency installation
- Use appropriate base images

### 3. Maintainability
- Use clear labels
- Document environment variables
- Follow consistent naming
- Include health checks
- Use semantic versioning

### 4. Development
- Enable hot-reloading
- Mount volumes for code
- Include development tools
- Configure debugging
- Set up linting

## Validation

### 1. Build and Test
```bash
# Build image
docker build -t your-app:latest .

# Run container
docker run -p 8000:8000 your-app:latest

# Test health endpoint
curl http://localhost:8000/health
```

### 2. Security Scan
```bash
# Install trivy
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin

# Scan image
trivy image your-app:latest
```

### 3. Size Check
```bash
# Check image size
docker images your-app:latest
```

## Common Issues and Solutions

### Issue 1: Large Image Size
- **Solution**: Use multi-stage builds and slim base images
- **Prevention**: Regularly clean up unused layers

### Issue 2: Slow Builds
- **Solution**: Optimize layer caching and dependency installation
- **Prevention**: Structure Dockerfile for optimal caching

### Issue 3: Security Vulnerabilities
- **Solution**: Regular security scans and updates
- **Prevention**: Use minimal base images and remove unnecessary tools

## Next Steps
- Set up dependency management (see Dependency-Management-Poetry-or-Requirements.md)
- Configure CI/CD pipeline (see GitHub-Actions-Build-and-Deploy.md)
- Implement container registry integration (see Container-Registry-Integration.md) 