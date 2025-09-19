# Smoke Testing Checklist for FastAPI Applications

## Objective
This checklist provides a comprehensive guide for performing smoke tests on FastAPI applications in a platform-agnostic manner. It covers infrastructure validation, application health checks, core functionality tests, and performance verification.

## Prerequisites
- Python 3.8+ installed
- FastAPI application deployed
- Application URL or endpoint
- Basic understanding of API testing

## 1. Infrastructure Validation

### 1.1 Check Application Status

```python
import httpx
import asyncio

async def check_application_status(base_url: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{base_url}/health")
            return response.status_code == 200
        except Exception as e:
            print(f"Error checking application status: {e}")
            return False

if __name__ == "__main__":
    base_url = "https://your-app.azurecontainerapps.io"
    status = asyncio.run(check_application_status(base_url))
    print(f"Application status: {'Healthy' if status else 'Unhealthy'}")
```

### 1.2 Verify Environment Variables

```python
import httpx
import asyncio

async def check_environment(base_url: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{base_url}/env")
            env_vars = response.json()
            required_vars = ["DATABASE_URL", "API_KEY", "ENVIRONMENT"]
            missing = [var for var in required_vars if var not in env_vars]
            if missing:
                print(f"Missing environment variables: {missing}")
                return False
            return True
        except Exception as e:
            print(f"Error checking environment: {e}")
            return False

if __name__ == "__main__":
    base_url = "https://your-app.azurecontainerapps.io"
    env_status = asyncio.run(check_environment(base_url))
    print(f"Environment status: {'Valid' if env_status else 'Invalid'}")
```

## 2. Application Health Checks

### 2.1 Basic Health Endpoint

```python
import httpx
import asyncio

async def test_health_endpoint(base_url: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{base_url}/health")
            return {
                "status": response.status_code == 200,
                "response_time": response.elapsed.total_seconds() * 1000,
                "body": response.json()
            }
        except Exception as e:
            print(f"Error testing health endpoint: {e}")
            return {"status": False, "error": str(e)}

if __name__ == "__main__":
    base_url = "https://your-app.azurecontainerapps.io"
    health = asyncio.run(test_health_endpoint(base_url))
    print(f"Health check: {health}")
```

### 2.2 Database Connectivity

```python
import httpx
import asyncio

async def test_database_connection(base_url: str):
    async with httpx.AsyncClient() as client:
        try:
            # Test Postgres connection
            response = await client.get(f"{base_url}/postgres/health")
            postgres_health = {
                "status": response.status_code == 200,
                "response_time": response.elapsed.total_seconds() * 1000,
                "body": response.json()
            }
            
            # Test Redis connection
            response = await client.get(f"{base_url}/redis/health")
            redis_health = {
                "status": response.status_code == 200,
                "response_time": response.elapsed.total_seconds() * 1000,
                "body": response.json()
            }
            
            return {
                "postgres": postgres_health,
                "redis": redis_health
            }
        except Exception as e:
            print(f"Error testing database connections: {e}")
            return {"error": str(e)}

if __name__ == "__main__":
    base_url = "https://your-app.azurecontainerapps.io"
    db_health = asyncio.run(test_database_connection(base_url))
    print(f"Database health: {db_health}")
```

## 3. Core Functionality Tests

### 3.1 API Endpoints

```python
import httpx
import asyncio
from typing import List, Dict

async def test_api_endpoints(base_url: str, endpoints: List[Dict]):
    results = []
    async with httpx.AsyncClient() as client:
        for endpoint in endpoints:
            try:
                if endpoint["method"] == "GET":
                    response = await client.get(f"{base_url}{endpoint['path']}")
                else:
                    response = await client.post(
                        f"{base_url}{endpoint['path']}",
                        json=endpoint.get("data", {})
                    )
                results.append({
                    "endpoint": endpoint["path"],
                    "method": endpoint["method"],
                    "status": response.status_code == 200,
                    "response_time": response.elapsed.total_seconds() * 1000
                })
            except Exception as e:
                results.append({
                    "endpoint": endpoint["path"],
                    "method": endpoint["method"],
                    "status": False,
                    "error": str(e)
                })
    return results

if __name__ == "__main__":
    base_url = "https://your-app.azurecontainerapps.io"
    endpoints = [
        {"path": "/api/v1/status", "method": "GET"},
        {"path": "/api/v1/data", "method": "POST", "data": {"test": "data"}}
    ]
    results = asyncio.run(test_api_endpoints(base_url, endpoints))
    for result in results:
        print(f"Endpoint {result['endpoint']}: {'Success' if result['status'] else 'Failed'}")
```

### 3.2 Authentication

```python
import httpx
import asyncio

async def test_authentication(base_url: str, api_key: str):
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {api_key}"}
        try:
            response = await client.get(
                f"{base_url}/api/v1/secure",
                headers=headers
            )
            return {
                "status": response.status_code == 200,
                "response_time": response.elapsed.total_seconds() * 1000
            }
        except Exception as e:
            print(f"Error testing authentication: {e}")
            return {"status": False, "error": str(e)}

if __name__ == "__main__":
    base_url = "https://your-app.azurecontainerapps.io"
    api_key = "your-api-key"
    auth = asyncio.run(test_authentication(base_url, api_key))
    print(f"Authentication test: {auth}")
```

## 4. Performance Checks

### 4.1 Response Time

```python
import httpx
import asyncio
import statistics
from typing import List

async def measure_response_times(base_url: str, num_requests: int = 10):
    times: List[float] = []
    async with httpx.AsyncClient() as client:
        for _ in range(num_requests):
            try:
                response = await client.get(f"{base_url}/health")
                times.append(response.elapsed.total_seconds() * 1000)
            except Exception as e:
                print(f"Error measuring response time: {e}")
    
    if times:
        return {
            "average": statistics.mean(times),
            "median": statistics.median(times),
            "p95": statistics.quantiles(times, n=20)[18]
        }
    return {"error": "No successful measurements"}

if __name__ == "__main__":
    base_url = "https://your-app.azurecontainerapps.io"
    times = asyncio.run(measure_response_times(base_url))
    print(f"Response times: {times}")
```

### 4.2 Concurrent Requests

```python
import httpx
import asyncio
from typing import List

async def test_concurrent_requests(base_url: str, num_requests: int = 10):
    async with httpx.AsyncClient() as client:
        tasks = []
        for _ in range(num_requests):
            task = client.get(f"{base_url}/health")
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        success_count = sum(1 for r in responses if isinstance(r, httpx.Response) and r.status_code == 200)
        return {
            "total_requests": num_requests,
            "successful_requests": success_count,
            "success_rate": (success_count / num_requests) * 100
        }

if __name__ == "__main__":
    base_url = "https://your-app.azurecontainerapps.io"
    results = asyncio.run(test_concurrent_requests(base_url))
    print(f"Concurrent request test: {results}")
```

## 5. Logging and Monitoring

### 5.1 Check Logs

```python
import httpx
import asyncio

async def check_application_logs(base_url: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{base_url}/logs")
            logs = response.json()
            error_logs = [log for log in logs if log["level"] == "ERROR"]
            return {
                "total_logs": len(logs),
                "error_logs": len(error_logs),
                "has_errors": len(error_logs) > 0
            }
        except Exception as e:
            print(f"Error checking logs: {e}")
            return {"error": str(e)}

if __name__ == "__main__":
    base_url = "https://your-app.azurecontainerapps.io"
    logs = asyncio.run(check_application_logs(base_url))
    print(f"Log check: {logs}")
```

### 5.2 Monitor Metrics

```python
import httpx
import asyncio

async def check_application_metrics(base_url: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{base_url}/metrics")
            metrics = response.json()
            return {
                "cpu_usage": metrics.get("cpu_usage"),
                "memory_usage": metrics.get("memory_usage"),
                "request_count": metrics.get("request_count")
            }
        except Exception as e:
            print(f"Error checking metrics: {e}")
            return {"error": str(e)}

if __name__ == "__main__":
    base_url = "https://your-app.azurecontainerapps.io"
    metrics = asyncio.run(check_application_metrics(base_url))
    print(f"Metrics check: {metrics}")
```

## 6. Validation Script

Create a comprehensive validation script that combines all the above tests:

```python
import httpx
import asyncio
from typing import Dict, List
import statistics
from datetime import datetime

class SmokeTest:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.results: Dict = {}

    async def run_all_tests(self):
        self.results["timestamp"] = datetime.now().isoformat()
        
        # Infrastructure tests
        self.results["application_status"] = await self.check_application_status()
        self.results["environment"] = await self.check_environment()
        
        # Health checks
        self.results["health_endpoint"] = await self.test_health_endpoint()
        self.results["database_health"] = await self.test_database_connection()
        
        # API tests
        endpoints = [
            {"path": "/api/v1/status", "method": "GET"},
            {"path": "/api/v1/data", "method": "POST", "data": {"test": "data"}}
        ]
        self.results["api_endpoints"] = await self.test_api_endpoints(endpoints)
        self.results["authentication"] = await self.test_authentication()
        
        # Performance tests
        self.results["response_times"] = await self.measure_response_times()
        self.results["concurrent_requests"] = await self.test_concurrent_requests()
        
        # Monitoring
        self.results["logs"] = await self.check_application_logs()
        self.results["metrics"] = await self.check_application_metrics()
        
        return self.results

    # Implement all the test methods from above...
    # (Methods would be implemented here)

if __name__ == "__main__":
    base_url = "https://your-app.azurecontainerapps.io"
    api_key = "your-api-key"
    
    smoke_test = SmokeTest(base_url, api_key)
    results = asyncio.run(smoke_test.run_all_tests())
    
    # Print results
    print("\nSmoke Test Results:")
    print("===================")
    for test, result in results.items():
        print(f"\n{test}:")
        print(result)
```

## Common Issues and Solutions

### Issue 1: Connection Timeouts
- **Solution**: Increase timeout settings in httpx client
- **Prevention**: Implement proper timeout handling

### Issue 2: Authentication Failures
- **Solution**: Verify API key and token generation
- **Prevention**: Implement proper error handling

### Issue 3: Performance Degradation
- **Solution**: Check resource allocation and scaling
- **Prevention**: Monitor metrics and set up alerts

## Best Practices

### 1. Testing Strategy
- Start with basic health checks
- Progress to core functionality
- Test performance under load
- Monitor system metrics
- Document test results

### 2. Error Handling
- Implement proper exception handling
- Log all errors
- Set up alerts for critical issues
- Document error patterns
- Create runbooks for common issues

### 3. Monitoring
- Track response times
- Monitor error rates
- Check resource usage
- Analyze logs
- Set up alerts

## Next Steps
1. Implement the validation script
2. Run smoke tests regularly
3. Monitor test results
4. Address any issues found
5. Update tests as needed 