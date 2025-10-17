# Stage 3 – Docker Basics# Docker Basics for Chainlit Deployment

In this stage you learn how to pack your Chainlit app into a container. Think of a container as a lunch box: the food (your code) and all utensils (your libraries) travel together so the meal works on any table.This guide introduces Docker fundamentals and demonstrates how to containerize a Chainlit application.

## What You Will Learn## What You'll Learn

- New words: **image**, **container**, and **registry**1. **Docker Basics**

- How to build an image with one command - What is Docker?

- How to run the image on your computer - Container vs Virtual Machine

- How to share it with Render or Railway later - Docker terminology

  - Basic Docker commands

## Before You Start

2. **Dockerfile Components**

- Install Docker Desktop from https://www.docker.com/products/docker-desktop - Base images

- Open Docker Desktop once so it finishes setup - Working directory

- Make sure Stage 1 passes locally; we reuse the same `main.py` - Environment variables

  - Copying files

--- - Installing dependencies

- Security best practices

## Step 1 – Look at the Files

3. **Docker Compose**

````- Development setup

03_docker_basics/   - Environment variables

├── Dockerfile   - Volume mounting

├── docker-compose.yml   - Port mapping

├── .dockerignore

├── main.py## Project Structure

├── requirements.txt```

└── README.md.

```├── Dockerfile         # Docker build instructions

├── docker-compose.yml # Docker Compose configuration

- `Dockerfile` tells Docker how to build the lunch box.├── .dockerignore     # Files to exclude from build

- `docker-compose.yml` lets you run it with hot reload while coding.├── main.py           # Application code

- `.dockerignore` keeps big or secret files out of the image.├── requirements.txt  # Python dependencies

└── README.md        # This file

Open each file once so the names feel familiar.```



---## Docker Concepts



## Step 2 – Build the Image### What is Docker?

Docker is a platform that enables you to package your application and all its dependencies into a standardized unit called a container. This ensures your application runs consistently across different environments.

```bash

cd 03_docker_basics### Key Terms

docker build -t chainlit-agent .- **Image**: A blueprint for creating containers

```- **Container**: A running instance of an image

- **Dockerfile**: Instructions for building an image

What happened?- **Docker Compose**: Tool for defining multi-container applications



- Docker downloaded `python:3.11-slim`.## Step-by-Step Guide

- It copied your app files inside the image.

- It installed the packages from `requirements.txt`.### 1. Building the Docker Image



You can check the new image with `docker images`.```bash

# Build the image

---docker build -t chainlit-app .



## Step 3 – Run the Container# View all images

docker images

```bash```

docker run \

  -p 8000:8000 \### 2. Running the Container

  -e OPENAI_API_KEY=$OPENAI_API_KEY \

  chainlit-agent```bash

```# Run the container

docker run -p 7860:7860 -e OPENAI_API_KEY=your-key chainlit-app

- `-p 8000:8000` maps the container port to your laptop port.

- `-e OPENAI_API_KEY=...` passes your secret into the container. You can also use `--env-file .env` if you saved it earlier.# View running containers

- Open [http://localhost:8000](http://localhost:8000) to chat.docker ps

````

Stop the container with `Ctrl + C` when you are done.

### 3. Using Docker Compose

---

````bash

## Step 4 – Use Docker Compose (Optional but Friendly)# Start the application

docker-compose up

```bash

docker compose up --build# Stop the application

```docker-compose down

````

Compose watches your files for changes and restarts the container when you save. Quit with `Ctrl + C`. Remove stopped containers with `docker compose down`.

### 4. Development with Hot Reload

---

````bash

## Step 5 – Share the Image (Bonus)# Start with hot reload

docker-compose up --build

When you feel ready, tag and push the image to Docker Hub or an internal registry:```



```bash## Dockerfile Explained

docker tag chainlit-agent yourname/chainlit-agent:v1

docker push yourname/chainlit-agent:v1```dockerfile

```# Base image

FROM python:3.9-slim

Render and Railway can pull that image and host it for you. Follow their dashboards to finish the deploy.

# Set working directory

---WORKDIR /app



## Quick Troubleshooting# Security: Create non-root user

RUN useradd -m -u 1000 user

- **“Cannot connect to Docker”** – open Docker Desktop so the engine is running.

- **“Unauthorized”** – the API key did not reach the container. Double-check `-e OPENAI_API_KEY=...`.# Install dependencies

- **“Port already in use”** – something else is on 8000. Change the first number, e.g., `-p 8001:8000`.COPY requirements.txt .

RUN pip install -r requirements.txt

You now know how containers work well enough to deploy your agent on any service that accepts Docker images. Head to Stage 4 to automate the deploy with GitHub Actions.

# Copy application
COPY . .

# Switch to non-root user
USER user

# Run application
CMD ["chainlit", "run", "main.py"]
````

## Docker Compose Explained

```yaml
version: "3.8"
services:
  chatbot:
    build: .
    ports:
      - "7860:7860" # Host:Container
    volumes:
      - .:/app # Local development
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
