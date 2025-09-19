#!/bin/bash
set -e

# Colors for better output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colorful status messages
status() {
    echo -e "${GREEN}[+] $1${NC}"
}

warning() {
    echo -e "${YELLOW}[!] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}" >&2
}

# Stop any existing containers
status "Cleaning up any existing containers..."
nerdctl rm -f chat-service-app chat-service-dapr agent-memory-service-app agent-memory-service-dapr redis 2>/dev/null || true
nerdctl network rm dapr-network 2>/dev/null || true

# Build the Docker images
status "Building chat-service image..."
(cd chat-service && nerdctl build -t chat-service:latest .)

status "Building agent-memory-service image..."
(cd agent_memory_service && nerdctl build -t agent-memory-service:latest .)

# Create a Docker network
status "Creating Docker network..."
nerdctl network create dapr-network

# Run Redis
status "Starting Redis container..."
nerdctl run -d --name redis \
  --network dapr-network \
  -p 6379:6379 \
  redis:7.0

# Wait for Redis to be ready
status "Waiting for Redis to be ready..."
sleep 3

# Run Agent Memory Service
status "Starting Agent Memory Service container..."
nerdctl run -d --name agent-memory-service-app \
  --network dapr-network \
  -p 8001:8001 \
  -e DAPR_HOST=agent-memory-service-dapr \
  -e MEMORY_SERVICE_HOST=agent-memory-service-app \
  agent-memory-service:latest

# Run Dapr sidecar for Agent Memory Service
status "Starting Dapr sidecar for Agent Memory Service..."
nerdctl run -d --name agent-memory-service-dapr \
  --network dapr-network \
  -p 3501:3501 \
  -v $(pwd)/components:/components \
  -e DAPR_HTTP_PORT=3501 \
  -e REDIS_HOST=redis \
  daprio/dapr:1.15.1 \
  ./daprd \
  --app-id agent-memory-service \
  --app-port 8001 \
  --dapr-http-port 3501 \
  --log-level debug \
  --components-path /components \
  --app-protocol http \
  --app-channel-address agent-memory-service-app

# Run Chat Service
status "Starting Chat Service container..."
nerdctl run -d --name chat-service-app \
  --network dapr-network \
  -p 8080:8080 \
  -e DAPR_HOST=chat-service-dapr \
  -e MEMORY_SERVICE_HOST=agent-memory-service-dapr \
  chat-service:latest

# Run Dapr sidecar for Chat Service
status "Starting Dapr sidecar for Chat Service..."
nerdctl run -d --name chat-service-dapr \
  --network dapr-network \
  -p 3500:3500 \
  -v $(pwd)/components:/components \
  -e DAPR_HTTP_PORT=3500 \
  -e REDIS_HOST=redis \
  daprio/dapr:1.15.1 \
  ./daprd \
  --app-id chat-service \
  --app-port 8080 \
  --dapr-http-port 3500 \
  --log-level debug \
  --components-path /components \
  --app-protocol http \
  --app-channel-address chat-service-app

# Verify the containers are running
status "Verifying containers are running..."
nerdctl ps

# Show connection info
status "All services are running!"
echo -e "${GREEN}------------------------------------${NC}"
echo -e "Chat Service: http://localhost:8080/chat/"
echo -e "Agent Memory Service: http://localhost:8001/memories/"
echo -e "${GREEN}------------------------------------${NC}"
echo -e "You