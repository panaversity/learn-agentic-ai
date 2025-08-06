# Basic Load Testing with Python

## Objective
This guide provides instructions for performing basic load testing on FastAPI applications using Python's built-in tools and popular testing libraries. This approach is platform-agnostic and works across Windows, macOS, and Linux.

## Prerequisites
- Python 3.8+ installed
- FastAPI application deployed
- Application URL or endpoint
- Basic understanding of load testing concepts

## Step-by-Step Instructions

### 1. Install Required Packages

```bash
# Install required packages using UV
uv add pytest pytest-asyncio httpx aiohttp locust
```

### 2. Create Basic Test Script

Create `load_test.py`:

```python
import asyncio
import httpx
from datetime import datetime
import statistics

async def test_endpoint(client: httpx.AsyncClient, url: str):
    start_time = datetime.now()
    response = await client.get(url)
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds() * 1000  # Convert to milliseconds
    return response.status_code, duration

async def run_load_test(base_url: str, num_requests: int = 100, concurrent_requests: int = 10):
    async with httpx.AsyncClient() as client:
        tasks = []
        for _ in range(num_requests):
            task = test_endpoint(client, f"{base_url}/health")
            tasks.append(task)
            if len(tasks) >= concurrent_requests:
                results = await asyncio.gather(*tasks)
                tasks = []
                # Process results
                status_codes = [r[0] for r in results]
                durations = [r[1] for r in results]
                print(f"Average response time: {statistics.mean(durations):.2f}ms")
                print(f"95th percentile: {statistics.quantiles(durations, n=20)[18]:.2f}ms")
                print(f"Success rate: {status_codes.count(200) / len(status_codes) * 100:.2f}%")

if __name__ == "__main__":
    base_url = "https://your-app.azurecontainerapps.io"
    asyncio.run(run_load_test(base_url))
```

### 3. Create Advanced Test Script

Create `advanced_load_test.py`:

```python
import asyncio
import httpx
from datetime import datetime
import statistics
from typing import List, Dict
import json

class LoadTest:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.results: List[Dict] = []

    async def test_endpoint(self, client: httpx.AsyncClient, endpoint: str, method: str = "GET", data: dict = None):
        start_time = datetime.now()
        try:
            if method == "GET":
                response = await client.get(f"{self.base_url}{endpoint}")
            else:
                response = await client.post(f"{self.base_url}{endpoint}", json=data)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds() * 1000
            return {
                "endpoint": endpoint,
                "status_code": response.status_code,
                "duration": duration,
                "success": response.status_code == 200
            }
        except Exception as e:
            return {
                "endpoint": endpoint,
                "status_code": 0,
                "duration": 0,
                "success": False,
                "error": str(e)
            }

    async def run_test_suite(self, num_requests: int = 100, concurrent_requests: int = 10):
        async with httpx.AsyncClient() as client:
            endpoints = [
                ("/health", "GET"),
                ("/api/v1/status", "GET"),
                ("/api/v1/data", "POST", {"test": "data"})
            ]
            
            for _ in range(num_requests):
                tasks = []
                for endpoint in endpoints:
                    if len(endpoint) == 2:
                        task = self.test_endpoint(client, endpoint[0], endpoint[1])
                    else:
                        task = self.test_endpoint(client, endpoint[0], endpoint[1], endpoint[2])
                    tasks.append(task)
                
                if len(tasks) >= concurrent_requests:
                    results = await asyncio.gather(*tasks)
                    self.results.extend(results)
                    self.print_stats()

    def print_stats(self):
        if not self.results:
            return
            
        success_rate = sum(1 for r in self.results if r["success"]) / len(self.results) * 100
        durations = [r["duration"] for r in self.results if r["success"]]
        
        print("\nTest Statistics:")
        print(f"Total requests: {len(self.results)}")
        print(f"Success rate: {success_rate:.2f}%")
        if durations:
            print(f"Average response time: {statistics.mean(durations):.2f}ms")
            print(f"95th percentile: {statistics.quantiles(durations, n=20)[18]:.2f}ms")

if __name__ == "__main__":
    base_url = "https://your-app.azurecontainerapps.io"
    test = LoadTest(base_url)
    asyncio.run(test.run_test_suite())
```

### 4. Run Basic Test

```bash
# Run basic test
python load_test.py

# Run with specific options
python load_test.py --num-requests 200 --concurrent-requests 20
```

### 5. Run Advanced Test

```bash
# Run advanced test
python advanced_load_test.py

# Run with specific options
python advanced_load_test.py --num-requests 500 --concurrent-requests 50
```

### 6. Using Locust for Distributed Testing

Create `locustfile.py`:

```python
from locust import HttpUser, task, between

class FastAPIUser(HttpUser):
    wait_time = between(1, 5)

    @task
    def health_check(self):
        self.client.get("/health")

    @task(3)
    def api_status(self):
        self.client.get("/api/v1/status")

    @task(2)
    def post_data(self):
        self.client.post("/api/v1/data", json={"test": "data"})
```

Run Locust:

```bash
# Start Locust web interface
locust -f locustfile.py --host=https://your-app.azurecontainerapps.io

# Run in headless mode
locust -f locustfile.py --host=https://your-app.azurecontainerapps.io --headless --users 100 --spawn-rate 10 --run-time 1m
```

## Validation

### 1. Monitor Application Metrics

```python
import httpx
import asyncio
from datetime import datetime, timedelta

async def monitor_metrics(base_url: str, duration_minutes: int = 5):
    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=duration_minutes)
    
    async with httpx.AsyncClient() as client:
        while datetime.now() < end_time:
            response = await client.get(f"{base_url}/metrics")
            metrics = response.json()
            print(f"Current metrics: {metrics}")
            await asyncio.sleep(30)  # Check every 30 seconds

if __name__ == "__main__":
    base_url = "https://your-app.azurecontainerapps.io"
    asyncio.run(monitor_metrics(base_url))
```

### 2. Check Application Logs

```python
import httpx
import asyncio

async def check_logs(base_url: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{base_url}/logs")
        logs = response.json()
        for log in logs:
            print(f"Log entry: {log}")

if __name__ == "__main__":
    base_url = "https://your-app.azurecontainerapps.io"
    asyncio.run(check_logs(base_url))
```

## Common Issues and Solutions

### Issue 1: High Latency
- **Solution**: Check resource allocation and scaling
- **Prevention**: Implement proper autoscaling

### Issue 2: Failed Requests
- **Solution**: Check application logs and configuration
- **Prevention**: Implement proper error handling

### Issue 3: Resource Exhaustion
- **Solution**: Monitor resource usage and adjust limits
- **Prevention**: Implement proper resource management

## Best Practices

### 1. Test Design
- Start with small load
- Gradually increase load
- Monitor system metrics
- Document test scenarios
- Use realistic data

### 2. Monitoring
- Track response times
- Monitor error rates
- Check resource usage
- Analyze logs
- Set up alerts

## Next Steps
- Implement smoke testing (see Smoke-Testing-Checklist.md)
- Set up monitoring and alerting
- Configure CI/CD pipeline 