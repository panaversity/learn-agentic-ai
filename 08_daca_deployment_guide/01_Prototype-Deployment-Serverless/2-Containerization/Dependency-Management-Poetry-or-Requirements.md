# Dependency Management with UV

## Objective
This guide provides best practices for managing Python dependencies using UV, a modern and fast Python package manager, ensuring reproducible builds and efficient dependency resolution.

## Prerequisites
- Python 3.11+ installed
- UV installed
- Basic understanding of Python packaging

## Step-by-Step Instructions

### 1. Initialize Project with UV

```bash
# Initialize a new project
uv --init --package your-package-name

# This creates:
# - pyproject.toml
# - README.md
# - src/your_package_name/
# - tests/
```

### 2. Configure pyproject.toml

```toml
[project]
name = "your-package-name"
version = "0.1.0"
description = "Your package description"
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]
dependencies = [
    "fastapi>=0.68.0",
    "uvicorn>=0.15.0",
    "pydantic>=1.8.0",
]
requires-python = ">=3.11"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
# UV specific configurations
resolver = "uv"
```

### 3. Add Development Dependencies

```bash
# Add development dependencies
uv add --dev pytest black isort mypy
```

### 4. Create Virtual Environment

```bash
# Create and activate virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 5. Install Dependencies

```bash
# Install all dependencies
uv pip install --system

# Install in development mode
uv pip install -e .
```

### 6. Update Dependencies

```bash
# Update all dependencies
uv pip install --upgrade --system

# Update specific package
uv pip install --upgrade fastapi
```

### 7. Generate Requirements Files

```bash
# Generate requirements.txt
uv pip freeze > requirements.txt

# Generate dev-requirements.txt
uv pip freeze --dev > dev-requirements.txt
```

## Best Practices

### 1. Dependency Management
- Use exact versions for production dependencies
- Group dependencies by purpose (core, dev, test)
- Document dependency purposes
- Regularly update dependencies
- Use dependency groups for different environments

### 2. Version Control
- Include pyproject.toml in version control
- Exclude virtual environment directory
- Include requirements.txt for compatibility
- Document version constraints
- Use semantic versioning

### 3. Security
- Regularly audit dependencies
- Use trusted package sources
- Monitor for vulnerabilities
- Keep dependencies updated
- Document security considerations

### 4. Performance
- Use UV for faster installations
- Minimize dependency count
- Optimize dependency resolution
- Use appropriate version constraints
- Leverage caching

## Validation

### 1. Check Dependencies
```bash
# List installed packages
uv pip list

# Check for outdated packages
uv pip list --outdated
```

### 2. Test Installation
```bash
# Test clean installation
uv pip install --system --no-cache-dir

# Verify package imports
python -c "import your_package_name"
```

### 3. Security Audit
```bash
# Install safety
uv pip install safety

# Run security check
safety check
```

## Common Issues and Solutions

### Issue 1: Dependency Conflicts
- **Solution**: Use UV's conflict resolution
- **Prevention**: Document version constraints

### Issue 2: Slow Installation
- **Solution**: Use UV's caching
- **Prevention**: Minimize dependency count

### Issue 3: Version Incompatibility
- **Solution**: Use appropriate version constraints
- **Prevention**: Test with different Python versions

## Integration with Docker

### 1. Dockerfile Integration
```dockerfile
# Install UV
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies
RUN uv pip install --system
```

### 2. Multi-stage Build
```dockerfile
# Build stage
FROM python:3.11-slim as builder

# Install UV and dependencies
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
COPY pyproject.toml ./
RUN uv pip install --system

# Production stage
FROM python:3.11-slim
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
```

## Next Steps
- Configure Dockerfile (see Dockerfile-Best-Practices.md)
- Set up CI/CD pipeline (see GitHub-Actions-Build-and-Deploy.md)
- Implement testing strategy 