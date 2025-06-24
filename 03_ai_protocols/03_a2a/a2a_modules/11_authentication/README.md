# Step 11: Authentication & Security 🔐

**Goal**: Implement secure authentication and authorization for A2A agent communication.

## 🎯 What You'll Learn

- A2A authentication mechanisms (OAuth2, JWT, API Keys)
- Extended Agent Cards with security metadata
- Secure agent-to-agent communication
- Authorization and permission patterns
- Enterprise security best practices

## 🔐 A2A Security Mechanisms

### 1. API Key Authentication
```
Authorization: Bearer <api_key>
Agent Card: Include authentication requirements
```

### 2. OAuth2 Flow
```
Client → Authorization Server → Access Token → Agent
Agent validates token and processes request
```

### 3. JWT Authentication
```
Client → JWT Token (signed) → Agent  
Agent verifies signature and extracts claims
```

### 4. Mutual TLS (mTLS)
```
Client Certificate ↔ Server Certificate
Bidirectional certificate validation
```

## 📁 Project Structure

```
11_authentication/
├── README.md                    # This guide
├── pyproject.toml              # UV project configuration
├── auth_server.py              # OAuth2/JWT authentication server
├── secure_agent.py             # Agent with authentication
├── api_key_agent.py            # API key-based authentication
├── jwt_agent.py                # JWT-based authentication
├── oauth_agent.py              # OAuth2-based authentication
├── mtls_agent.py               # Mutual TLS authentication
├── auth_client.py              # Client with authentication
├── test_auth.py                # Test authentication flows
└── requirements.txt           # Dependencies
```

## 🚀 Implementation

### 1. Setup Project
```bash
cd 11_authentication
uv sync
```

### 2. Start Authentication Server
```bash
uv run python auth_server.py
# Runs on http://localhost:9000
# Provides OAuth2/JWT endpoints
```

### 3. Start Secure Agents (Multiple Terminals)
```bash
# Terminal 2: API Key Agent
uv run python api_key_agent.py
# Runs on http://localhost:8001

# Terminal 3: JWT Agent  
uv run python jwt_agent.py
# Runs on http://localhost:8002

# Terminal 4: OAuth2 Agent
uv run python oauth_agent.py
# Runs on http://localhost:8003
```

### 4. Test Authentication
```bash
# Terminal 5: Test Client
uv run python test_auth.py

# Or manual testing with authentication
curl -X POST http://localhost:8001/a2a/message/send \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_api_key_here" \
  -d '{"method": "message/send", "params": {"message": {"role": "user", "parts": [{"text": "Hello secure agent"}]}}}'
```

## 🔧 Authentication Patterns

### Extended Agent Cards
Agent Cards with authentication metadata:
```json
{
  "agent_id": "secure_math_agent",
  "name": "Secure Math Agent",
  "description": "Math agent with authentication",
  "skills": ["mathematics", "calculations"],
  "endpoints": {
    "a2a": "http://localhost:8001/a2a"
  },
  "authentication": {
    "required": true,
    "methods": ["api_key", "oauth2", "jwt"],
    "oauth2": {
      "authorization_url": "http://localhost:9000/auth",
      "token_url": "http://localhost:9000/token",
      "scopes": ["agent:read", "agent:write"]
    },
    "api_key": {
      "header": "Authorization",
      "format": "Bearer {key}"
    }
  },
  "security": {
    "tls_required": true,
    "rate_limits": {
      "requests_per_minute": 100
    }
  }
}
```

### API Key Authentication
```python
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if request.url.path.startswith("/a2a"):
        auth_header = request.headers.get("authorization")
        if not auth_header or not validate_api_key(auth_header):
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid or missing API key"}
            )
    return await call_next(request)
```

### JWT Authentication Flow
```
1. Client → Auth Server: credentials
2. Auth Server → Client: JWT token (signed)
3. Client → Agent: request + JWT token
4. Agent → validates JWT signature and claims
5. Agent → processes request if valid
```

### OAuth2 Flow
```
1. Client → Auth Server: client_credentials
2. Auth Server → Client: access_token  
3. Client → Agent: request + access_token
4. Agent → Auth Server: validate token
5. Agent → processes request if token valid
```

## 🎯 Testing Scenarios

### Manual Authentication Testing
```bash
# 1. Get API Key (simulate registration)
curl -X POST http://localhost:9000/register \
  -H "Content-Type: application/json" \
  -d '{"client_id": "test_client", "name": "Test Client"}'

# 2. Test API Key Authentication
curl -X POST http://localhost:8001/a2a/message/send \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <api_key>" \
  -d '{"method": "message/send", "params": {"message": {"role": "user", "parts": [{"text": "Calculate 2+2"}]}}}'

# 3. Get OAuth2 Token
curl -X POST http://localhost:9000/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&client_id=test_client&client_secret=secret"

# 4. Test OAuth2 Authentication
curl -X POST http://localhost:8003/a2a/message/send \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <oauth_token>" \
  -d '{"method": "message/send", "params": {"message": {"role": "user", "parts": [{"text": "Hello OAuth agent"}]}}}'
```

### Automated Security Testing
```bash
uv run python test_auth.py
```

## 🔍 Expected Results

### Successful Authentication
```json
{
  "id": "req_001",
  "result": {
    "message": {
      "role": "agent",
      "parts": [{"text": "Hello! I'm a secure agent. Your request has been authenticated."}]
    },
    "authentication": {
      "method": "jwt",
      "user_id": "client_123",
      "scopes": ["agent:read", "agent:write"]
    }
  }
}
```

### Authentication Failure
```json
{
  "id": "req_002",
  "error": {
    "code": 401,
    "message": "Authentication failed",
    "details": "Invalid or expired token"
  }
}
```

### Extended Agent Card Response
```json
{
  "agent_id": "secure_agent_001",
  "authentication": {
    "required": true,
    "methods": ["api_key", "oauth2"],
    "oauth2": {
      "authorization_url": "http://localhost:9000/auth",
      "token_url": "http://localhost:9000/token"
    }
  },
  "rate_limits": {
    "authenticated": "100/minute",
    "anonymous": "0/minute"
  }
}
```

## 🛡️ Security Best Practices

### Authentication
- **Strong Token Generation**: Use cryptographically secure random tokens
- **Token Expiration**: Implement reasonable token lifetimes
- **Scope-Based Access**: Limit permissions with OAuth2 scopes
- **Secure Storage**: Never log or expose authentication credentials

### Authorization
- **Principle of Least Privilege**: Grant minimum required permissions
- **Role-Based Access**: Implement role-based authorization
- **Resource-Level Permissions**: Control access to specific capabilities
- **Audit Logging**: Log all authentication and authorization events

### Transport Security
- **TLS Everywhere**: Require HTTPS/TLS for all communications
- **Certificate Validation**: Properly validate TLS certificates
- **HSTS Headers**: Use HTTP Strict Transport Security
- **Certificate Pinning**: Pin certificates for critical connections

### Rate Limiting & DoS Protection
- **Per-Client Limits**: Implement per-client rate limiting
- **Adaptive Throttling**: Increase limits for authenticated users
- **Circuit Breakers**: Protect against cascading failures
- **Request Validation**: Validate all input parameters

## 🌟 Real-World Security Patterns

### Enterprise Agent Mesh
- **Service Mesh Security**: Istio/Envoy with mTLS
- **Identity Federation**: SAML/OIDC integration
- **Zero Trust Architecture**: Verify every request
- **Policy as Code**: Automated security policy enforcement

### Multi-Tenant Agent Systems
- **Tenant Isolation**: Separate data and processing
- **Resource Quotas**: Limit resource usage per tenant
- **Audit Trails**: Complete activity logging
- **Data Encryption**: Encrypt data at rest and in transit

### Regulatory Compliance
- **GDPR Compliance**: Data protection and privacy
- **SOC 2**: Security and availability controls
- **HIPAA**: Healthcare data protection
- **Financial Services**: PCI DSS compliance

## 🔧 Advanced Security Features

### Dynamic Authentication
- **Context-Aware Auth**: Authentication based on request context
- **Risk-Based Auth**: Additional verification for high-risk requests
- **Adaptive MFA**: Multi-factor authentication when needed
- **Behavioral Analysis**: Detect anomalous agent behavior

### Federated Agent Security
- **Cross-Domain Trust**: Establish trust between agent domains
- **Token Exchange**: Secure token exchange protocols
- **Delegation Patterns**: Secure agent delegation
- **Trust Hierarchies**: Multi-level trust relationships

### Security Monitoring
- **Real-Time Monitoring**: Monitor authentication events
- **Anomaly Detection**: Detect unusual access patterns
- **Security Dashboards**: Visualize security metrics
- **Incident Response**: Automated security incident handling

## 📖 Next Steps

- **Step 12**: [Enterprise Features](../12_enterprise_features/) - Production deployment and monitoring

## 📚 References

- [A2A Security Specification](https://google-a2a.github.io/A2A/specification/#security)
- [OAuth 2.0 RFC](https://tools.ietf.org/html/rfc6749)
- [JWT RFC](https://tools.ietf.org/html/rfc7519)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework) 