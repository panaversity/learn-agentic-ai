#!/bin/bash
set -e

# Colors for better output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}[+] Stopping all containers...${NC}"
nerdctl rm -f chat-service-app chat-service-dapr agent-memory-service-app agent-memory-service-dapr redis 2>/dev/null || true
nerdctl network rm dapr-network 2>/dev/null || true

echo -e "${GREEN}[+] All containers stopped!${NC}"