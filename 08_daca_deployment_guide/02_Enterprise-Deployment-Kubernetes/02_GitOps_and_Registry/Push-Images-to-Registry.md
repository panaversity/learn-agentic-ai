# Push Images to Registry

## Objective
This guide provides step-by-step instructions for building, tagging, and pushing container images to a container registry, ensuring proper versioning and security practices.

## Prerequisites
- Docker or Podman installed
- Access to a container registry (e.g., Docker Hub, GitHub Container Registry, or private registry)
- Dockerfile for your application
- Registry credentials configured

## Step-by-Step Instructions

### 1. Build Container Image

#### 1.1 Build with Docker
```bash
# Build image with Docker
docker build -t your-app:latest .

# Build with specific Dockerfile
docker build -t your-app:latest -f Dockerfile.prod .

# Build with build arguments
docker build -t your-app:latest --build-arg VERSION=1.0.0 .
```

#### 1.2 Build with Podman
```bash
# Build image with Podman
podman build -t your-app:latest .

# Build with specific Dockerfile
podman build -t your-app:latest -f Dockerfile.prod .

# Build with build arguments
podman build -t your-app:latest --build-arg VERSION=1.0.0 .
```

### 2. Tag Images

#### 2.1 Tag for Registry
```bash
# Tag for Docker Hub
docker tag your-app:latest username/your-app:latest

# Tag for GitHub Container Registry
docker tag your-app:latest ghcr.io/username/your-app:latest

# Tag for private registry
docker tag your-app:latest registry.example.com/your-app:latest
```

#### 2.2 Version Tagging
```bash
# Tag with version
docker tag your-app:latest username/your-app:1.0.0

# Tag with commit hash
docker tag your-app:latest username/your-app:$(git rev-parse --short HEAD)

# Tag with environment
docker tag your-app:latest username/your-app:production
```

### 3. Push to Registry

#### 3.1 Push to Docker Hub
```bash
# Login to Docker Hub
docker login

# Push image
docker push username/your-app:latest
docker push username/your-app:1.0.0
```

#### 3.2 Push to GitHub Container Registry
```bash
# Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u username --password-stdin

# Push image
docker push ghcr.io/username/your-app:latest
docker push ghcr.io/username/your-app:1.0.0
```

#### 3.3 Push to Private Registry
```bash
# Login to private registry
docker login registry.example.com

# Push image
docker push registry.example.com/your-app:latest
docker push registry.example.com/your-app:1.0.0
```

### 4. Multi-Architecture Builds

#### 4.1 Create Buildx Builder
```bash
# Create and use buildx builder
docker buildx create --use

# Build multi-arch image
docker buildx build --platform linux/amd64,linux/arm64 -t username/your-app:latest --push .
```

#### 4.2 Verify Multi-Arch Build
```bash
# Check image manifest
docker buildx imagetools inspect username/your-app:latest
```

## Validation

### 1. Verify Image Build
```bash
# List local images
docker images

# Inspect image
docker inspect username/your-app:latest
```

### 2. Test Image
```bash
# Run container
docker run -d -p 8080:8080 username/your-app:latest

# Check container logs
docker logs $(docker ps -q --filter ancestor=username/your-app:latest)
```

### 3. Verify Registry Push
```bash
# Pull image from registry
docker pull username/your-app:latest

# Run pulled image
docker run -d -p 8080:8080 username/your-app:latest
```

## Common Issues and Solutions

### Issue 1: Authentication Failures
- **Solution**: Verify registry credentials
- **Prevention**: Use secure credential storage

### Issue 2: Push Size Limits
- **Solution**: Optimize image size
- **Prevention**: Use multi-stage builds

### Issue 3: Network Issues
- **Solution**: Check network connectivity
- **Prevention**: Use reliable network connection

## Best Practices

### 1. Image Building
- Use multi-stage builds
- Minimize layers
- Remove unnecessary files
- Use specific base images
- Scan for vulnerabilities

### 2. Tagging Strategy
- Semantic versioning
- Environment tags
- Commit hash tags
- Latest tag with caution
- Clear documentation

### 3. Security
- Use non-root users
- Scan for vulnerabilities
- Sign images
- Use private registries
- Regular updates

## Next Steps
- Set up automated builds
- Configure image scanning
- Implement image signing
- Set up registry monitoring
