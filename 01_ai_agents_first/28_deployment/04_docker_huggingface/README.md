# Deploying Chainlit with Docker to Hugging Face Spaces

This guide demonstrates how to deploy a Dockerized Chainlit application to Hugging Face Spaces using production-ready configurations.

## What You'll Learn

1. **Production Docker Setup**
   - Multi-stage builds
   - Optimizing image size
   - Security considerations
   - Environment configuration

2. **Hugging Face Spaces Integration**
   - Space configuration
   - Docker deployment
   - Environment variables
   - Secrets management

3. **Production Best Practices**
   - Health checks
   - Logging
   - Error handling
   - Performance optimization

## Project Structure
```
.
├── Dockerfile         # Multi-stage Dockerfile
├── .dockerignore     # Build exclusions
├── main.py           # Application code
├── requirements.txt  # Production dependencies
└── README.md        # This file
```

## Hugging Face Spaces Setup

1. **Create a New Space**
   - Go to [Hugging Face Spaces](https://huggingface.co/spaces)
   - Click "Create new Space"
   - Select "Docker" as the SDK
   - Choose your Space name and visibility

2. **Configure Repository**
   ```bash
   # Clone your Space
   git clone https://huggingface.co/spaces/your-username/your-space-name
   
   # Copy your application files
   cp -r * /path/to/space/
   
   # Push to Hugging Face
   git add .
   git commit -m "Initial Docker deployment"
   git push
   ```

3. **Set Up Secrets**
   - Go to Space Settings
   - Add `OPENAI_API_KEY` as a secret
   - Add any other required secrets

## Dockerfile Explained

```dockerfile
# Builder stage
FROM python:3.9-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

# Runtime stage
FROM python:3.9-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.9/ /usr/local/lib/python3.9/
COPY . .
```

Key features:
- Multi-stage build for smaller image
- Non-root user for security
- Production-ready configuration
- Optimized layer caching

## Environment Variables

Required variables for production:
```bash
OPENAI_API_KEY=your-api-key
PORT=7860  # Hugging Face Spaces port
```

## Deployment Steps

1. **Prepare Your Application**
   ```bash
   # Test locally first
   docker build -t chainlit-app .
   docker run -p 7860:7860 chainlit-app
   ```

2. **Push to Hugging Face**
   - Commit all files including Dockerfile
   - Push to your Space repository
   - Hugging Face will automatically build and deploy

3. **Monitor Deployment**
   - Check build logs in Space
   - Verify application health
   - Test functionality

## Production Considerations

1. **Security**
   - Use multi-stage builds
   - Run as non-root user
   - Secure environment variables
   - Regular security updates

2. **Performance**
   - Optimize Docker image size
   - Enable caching
   - Configure resource limits
   - Monitor memory usage

3. **Maintenance**
   - Regular dependency updates
   - Log monitoring
   - Backup strategies
   - Version control

## Troubleshooting

1. **Build Issues**
   - Check Space build logs
   - Verify Dockerfile syntax
   - Check resource limits
   - Validate dependencies

2. **Runtime Issues**
   - Check application logs
   - Verify environment variables
   - Check port configuration
   - Monitor resource usage

3. **Common Problems**
   - Memory limits exceeded
   - Missing environment variables
   - Port conflicts
   - Permission issues

## Best Practices

1. **Docker Image**
   - Use specific version tags
   - Minimize layer count
   - Optimize caching
   - Regular base image updates

2. **Security**
   - Regular security scans
   - Dependency updates
   - Secret management
   - Access control

3. **Monitoring**
   - Application health checks
   - Resource monitoring
   - Error tracking
   - Performance metrics

## Next Steps

1. **Advanced Features**
   - Custom domain setup
   - CI/CD integration
   - Automated testing
   - Scaling strategies

2. **Optimization**
   - Performance tuning
   - Resource optimization
   - Caching strategies
   - Load testing

## Resources

- [Hugging Face Spaces Documentation](https://huggingface.co/docs/hub/spaces)
- [Docker Production Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Container Security Guide](https://docs.docker.com/develop/security-best-practices/)
- [Chainlit Documentation](https://docs.chainlit.io) 