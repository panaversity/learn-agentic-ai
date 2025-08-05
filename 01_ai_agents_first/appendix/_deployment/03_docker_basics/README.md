# Docker Basics for Chainlit Deployment

This guide introduces Docker fundamentals and demonstrates how to containerize a Chainlit application.

## What You'll Learn

1. **Docker Basics**
   - What is Docker?
   - Container vs Virtual Machine
   - Docker terminology
   - Basic Docker commands

2. **Dockerfile Components**
   - Base images
   - Working directory
   - Environment variables
   - Copying files
   - Installing dependencies
   - Security best practices

3. **Docker Compose**
   - Development setup
   - Environment variables
   - Volume mounting
   - Port mapping

## Project Structure
```
.
├── Dockerfile         # Docker build instructions
├── docker-compose.yml # Docker Compose configuration
├── .dockerignore     # Files to exclude from build
├── main.py           # Application code
├── requirements.txt  # Python dependencies
└── README.md        # This file
```

## Docker Concepts

### What is Docker?
Docker is a platform that enables you to package your application and all its dependencies into a standardized unit called a container. This ensures your application runs consistently across different environments.

### Key Terms
- **Image**: A blueprint for creating containers
- **Container**: A running instance of an image
- **Dockerfile**: Instructions for building an image
- **Docker Compose**: Tool for defining multi-container applications

## Step-by-Step Guide

### 1. Building the Docker Image

```bash
# Build the image
docker build -t chainlit-app .

# View all images
docker images
```

### 2. Running the Container

```bash
# Run the container
docker run -p 7860:7860 -e OPENAI_API_KEY=your-key chainlit-app

# View running containers
docker ps
```

### 3. Using Docker Compose

```bash
# Start the application
docker-compose up

# Stop the application
docker-compose down
```

### 4. Development with Hot Reload

```bash
# Start with hot reload
docker-compose up --build
```

## Dockerfile Explained

```dockerfile
# Base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Security: Create non-root user
RUN useradd -m -u 1000 user

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY . .

# Switch to non-root user
USER user

# Run application
CMD ["chainlit", "run", "main.py"]
```

## Docker Compose Explained

```yaml
version: '3.8'
services:
  chatbot:
    build: .
    ports:
      - "7860:7860"    # Host:Container
    volumes:
      - .:/app         # Local development
    environment:
      - OPENAI_API_KEY # From .env file
```

## Best Practices

1. **Security**
   - Use non-root users
   - Minimize image size
   - Keep secrets in environment variables

2. **Performance**
   - Use .dockerignore
   - Layer caching
   - Multi-stage builds

3. **Development**
   - Use Docker Compose
   - Enable hot reload
   - Mount volumes for local development

## Common Commands

```bash
# Build image
docker build -t app-name .

# Run container
docker run app-name

# List containers
docker ps

# Stop container
docker stop container-id

# Remove container
docker rm container-id

# View logs
docker logs container-id

# Execute command in container
docker exec -it container-id bash
```

## Troubleshooting

1. **Container won't start**
   - Check logs: `docker logs container-id`
   - Verify port mapping
   - Check environment variables

2. **Changes not reflecting**
   - Rebuild image: `docker-compose up --build`
   - Check volume mounting
   - Clear Docker cache

3. **Permission issues**
   - Verify user permissions
   - Check file ownership
   - Review volume mounts

## Next Steps

After mastering these basics, you'll be ready to:
1. Deploy to production environments
2. Implement multi-container applications
3. Use Docker in CI/CD pipelines
4. Optimize container performance

## Resources

- [Official Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Docker Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/) 