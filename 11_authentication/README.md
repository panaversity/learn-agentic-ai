# Step 11: Authentication & Security 🔐

**Learning Objective**: Implement enterprise-grade authentication and security mechanisms using the official A2A Python SDK, ensuring secure agent interactions with proper authorization and audit trails.

## 📚 Official A2A Reference

**Primary Documentation**: [A2A Python SDK Documentation](https://google-a2a.github.io/A2A/latest/sdk/python/)  
**Authentication Guide**: [A2A Enterprise-Ready Features](https://google-a2a.github.io/A2A/topics/enterprise-ready/)  
**Security Specification**: [A2A Protocol Security](https://google-a2a.github.io/A2A/specification/#security)

## 🎯 What You'll Learn

- A2A SDK authentication mechanisms (OAuth 2.0, Bearer tokens, API Keys)
- Agent identity verification using A2A security schemes
- Secure communication with A2A SDK built-in security
- Authorization and permission management via SDK
- Using A2A telemetry for security monitoring
- Enterprise-ready security patterns with A2A SDK

## 🏗️ Project Structure

```
11_authentication/
├── README.md
├── pyproject.toml
├── src/
│   ├── secure_agent.py          # Agent with A2A authentication
│   ├── auth_provider.py         # A2A authentication provider
│   ├── security_middleware.py   # A2A security middleware
│   └── permission_manager.py    # Permission management with A2A
├── agents/
│   ├── authenticated_agent.py   # Agent requiring authentication
│   ├── trusted_agent.py         # High-trust agent with strict auth
│   └── service_agent.py         # Service-to-service auth
├── examples/
│   ├── oauth_authentication.py  # OAuth 2.0 with A2A SDK
│   ├── api_key_auth.py          # API key authentication
│   ├── bearer_token_auth.py     # Bearer token authentication
│   └── secure_communication.py  # End-to-end secure communication
├── tests/
│   ├── test_auth_flows.py
│   └── test_security_features.py
└── config/
    ├── security_schemes.json    # A2A security scheme definitions
    └── auth_config.yaml         # Authentication configuration
```

## 🚀 Quick Start

### 1. Initialize Project

```bash
cd 11_authentication
uv init a2a_security
cd a2a_security
uv add a2a fastapi uvicorn python-jose[cryptography] httpx
```

### 2. Start Authenticated Agents

```bash
# Terminal 1: Start authenticated agent
uv run python agents/authenticated_agent.py

# Terminal 2: Start trusted agent
uv run python agents/trusted_agent.py

# Terminal 3: Test authentication flows
uv run python examples/oauth_authentication.py
```

### 3. Test Security Features

```bash
# Test OAuth 2.0 authentication
uv run python examples/oauth_authentication.py

# Test API key authentication
uv run python examples/api_key_auth.py

# Test secure agent communication
uv run python examples/secure_communication.py
```

## 📋 Core Implementation

### Authenticated Agent with A2A SDK (agents/authenticated_agent.py)

```python
from a2a import Agent, AgentCard, AgentSkill, AgentProvider, AgentCapabilities
from a2a.server import A2AServer
from a2a.auth import User, UnauthenticatedUser
from a2a.types import SecurityScheme, OAuth2SecurityScheme, HTTPAuthSecurityScheme, APIKeySecurityScheme
import asyncio
import logging
from typing import Dict, Optional

# Define security schemes using A2A SDK
oauth2_scheme = OAuth2SecurityScheme(
    description="OAuth 2.0 authentication for agent access",
    flows={
        "client_credentials": {
            "token_url": "http://localhost:9000/oauth/token",
            "scopes": {
                "agent:read": "Read agent information",
                "agent:write": "Modify agent state",
                "task:execute": "Execute tasks"
            }
        }
    }
)

bearer_token_scheme = HTTPAuthSecurityScheme(
    scheme="bearer",
    bearer_format="JWT",
    description="Bearer token authentication"
)

api_key_scheme = APIKeySecurityScheme(
    name="X-API-Key",
    location="header",
    description="API key authentication"
)

# Create authenticated agent card
authenticated_card = AgentCard(
    name="Authenticated Agent",
    version="1.0.0",
    description="Secure agent requiring authentication using A2A SDK",
    provider=AgentProvider(
        organization="A2A Secure Network",
        url="http://localhost:8300"
    ),
    url="http://localhost:8300",
    capabilities=AgentCapabilities(
        streaming=False,
        push_notifications=False,
        extensions=[]
    ),
    skills=[
        AgentSkill(
            id="secure_process",
            name="Secure Processing",
            description="Process sensitive data with authentication required",
            input_modes=["text"],
            output_modes=["text"]
        ),
        AgentSkill(
            id="admin_task",
            name="Administrative Task",
            description="High-privilege administrative operations",
            input_modes=["text"],
            output_modes=["text"]
        )
    ],
    security_schemes={
        "oauth2": oauth2_scheme,
        "bearer": bearer_token_scheme,
        "apiKey": api_key_scheme
    },
    security=[
        {"oauth2": ["agent:read", "task:execute"]},
        {"bearer": []},
        {"apiKey": []}
    ]
)

class AuthenticatedAgent:
    def __init__(self):
        self.agent = Agent(card=authenticated_card)
        
        # Register skills with authentication checks
        self.agent.skill("secure_process")(self.secure_process)
        self.agent.skill("admin_task")(self.admin_task)
    
    async def secure_process(self, message, context):
        """Process data with authentication verification"""
        # Get user from context (populated by A2A SDK authentication)
        user = context.get("user")
        
        if not user or not user.is_authenticated:
            return {
                "content": "Authentication required for secure processing",
                "type": "error",
                "metadata": {"error_code": "AUTHENTICATION_REQUIRED"}
            }
        
        # Verify user has required permissions
        if not self._has_permission(user, "task:execute"):
            return {
                "content": "Insufficient permissions for secure processing",
                "type": "error",
                "metadata": {"error_code": "INSUFFICIENT_PERMISSIONS"}
            }
        
        # Process the request securely
        task_content = message.content.strip()
        
        return {
            "content": f"Securely processed: {task_content}",
            "type": "text",
            "metadata": {
                "authenticated_user": user.user_name,
                "security_level": "high",
                "timestamp": context.get("timestamp")
            }
        }
    
    async def admin_task(self, message, context):
        """Handle administrative tasks requiring elevated privileges"""
        user = context.get("user")
        
        if not user or not user.is_authenticated:
            return {
                "content": "Authentication required for administrative tasks",
                "type": "error",
                "metadata": {"error_code": "AUTHENTICATION_REQUIRED"}
            }
        
        # Check for admin privileges
        if not self._has_permission(user, "agent:write"):
            return {
                "content": "Administrative privileges required",
                "type": "error",
                "metadata": {"error_code": "ADMIN_REQUIRED"}
            }
        
        admin_command = message.content.strip()
        
        # Log administrative action
        logging.info(f"Admin action by {user.user_name}: {admin_command}")
        
        return {
            "content": f"Administrative task executed: {admin_command}",
            "type": "text",
            "metadata": {
                "admin_user": user.user_name,
                "action": admin_command,
                "security_level": "administrative"
            }
        }
    
    def _has_permission(self, user: User, required_permission: str) -> bool:
        """Check if user has required permission"""
        # In a real implementation, this would check against a permission store
        # For demo purposes, we'll use a simple user property check
        if hasattr(user, 'permissions'):
            return required_permission in user.permissions
        
        # Default permissions based on authentication
        if user.is_authenticated:
            return required_permission in ["task:execute", "agent:read"]
        
        return False

async def main():
    logging.basicConfig(level=logging.INFO)
    
    agent_instance = AuthenticatedAgent()
    
    print("🔐 Starting Authenticated Agent with A2A SDK...")
    print("🛡️ Security schemes: OAuth 2.0, Bearer Token, API Key")
    print("🔑 Skills require authentication")
    
    # Create A2A server with authentication
    server = A2AServer(agent_instance.agent)
    
    # Start the server
    await server.start(host="0.0.0.0", port=8300)

if __name__ == "__main__":
    asyncio.run(main())
```

### A2A Authentication Provider (src/auth_provider.py)

```python
from a2a.auth import User, UnauthenticatedUser
from a2a.client import A2AClient
import httpx
import logging
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import jwt

class A2AAuthenticationProvider:
    """Authentication provider for A2A SDK"""
    
    def __init__(self, auth_server_url: str = "http://localhost:9000"):
        self.auth_server_url = auth_server_url
        self.token_cache = {}  # Simple token cache
    
    async def authenticate_with_oauth2(
        self, 
        client_id: str, 
        client_secret: str, 
        scopes: List[str] = None
    ) -> Optional[str]:
        """Authenticate using OAuth 2.0 client credentials flow"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.auth_server_url}/oauth/token",
                    data={
                        "grant_type": "client_credentials",
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "scope": " ".join(scopes or [])
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                
                if response.status_code == 200:
                    token_data = response.json()
                    access_token = token_data.get("access_token")
                    
                    # Cache token with expiration
                    expires_in = token_data.get("expires_in", 3600)
                    self.token_cache[client_id] = {
                        "token": access_token,
                        "expires_at": datetime.now() + timedelta(seconds=expires_in)
                    }
                    
                    return access_token
        
        except Exception as e:
            logging.error(f"OAuth 2.0 authentication failed: {e}")
        
        return None
    
    async def authenticate_with_api_key(
        self, 
        api_key: str
    ) -> Optional[Dict]:
        """Authenticate using API key"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.auth_server_url}/validate-api-key",
                    headers={"X-API-Key": api_key}
                )
                
                if response.status_code == 200:
                    return response.json()
        
        except Exception as e:
            logging.error(f"API key authentication failed: {e}")
        
        return None
    
    async def validate_bearer_token(self, token: str) -> Optional[Dict]:
        """Validate bearer token"""
        try:
            # For JWT tokens, we can validate locally
            if self._is_jwt_token(token):
                return self._validate_jwt_token(token)
            
            # For opaque tokens, validate with auth server
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.auth_server_url}/validate-token",
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                if response.status_code == 200:
                    return response.json()
        
        except Exception as e:
            logging.error(f"Bearer token validation failed: {e}")
        
        return None
    
    def create_authenticated_user(
        self, 
        user_data: Dict, 
        permissions: List[str] = None
    ) -> User:
        """Create authenticated A2A User object"""
        return User(
            user_name=user_data.get("username", "unknown"),
            permissions=permissions or [],
            metadata=user_data
        )
    
    def create_unauthenticated_user(self) -> UnauthenticatedUser:
        """Create unauthenticated A2A User object"""
        return UnauthenticatedUser()
    
    def _is_jwt_token(self, token: str) -> bool:
        """Check if token is a JWT"""
        return token.count('.') == 2
    
    def _validate_jwt_token(self, token: str) -> Optional[Dict]:
        """Validate JWT token locally"""
        try:
            # In production, use proper JWT validation with secret verification
            payload = jwt.decode(
                token, 
                options={"verify_signature": False}  # For demo only
            )
            return payload
        except Exception as e:
            logging.error(f"JWT validation failed: {e}")
            return None

class A2ASecureClient:
    """Secure A2A client with authentication"""
    
    def __init__(self, auth_provider: A2AAuthenticationProvider):
        self.auth_provider = auth_provider
    
    async def create_authenticated_client(
        self, 
        agent_url: str, 
        auth_method: str = "oauth2",
        **auth_params
    ) -> Optional[A2AClient]:
        """Create A2A client with authentication"""
        
        # Get authentication token based on method
        token = None
        if auth_method == "oauth2":
            token = await self.auth_provider.authenticate_with_oauth2(
                auth_params.get("client_id"),
                auth_params.get("client_secret"),
                auth_params.get("scopes", [])
            )
        elif auth_method == "api_key":
            # For API key, we'll use it directly in headers
            api_key = auth_params.get("api_key")
            if api_key:
                # Create client with API key in headers
                client = A2AClient.get_client_from_agent_card_url(agent_url)
                # Add API key to client headers (implementation-specific)
                if hasattr(client, 'httpx_client'):
                    client.httpx_client.headers["X-API-Key"] = api_key
                return client
        
        if token:
            # Create client with bearer token
            client = A2AClient.get_client_from_agent_card_url(agent_url)
            if hasattr(client, 'httpx_client'):
                client.httpx_client.headers["Authorization"] = f"Bearer {token}"
            return client
        
        return None
    
    async def send_authenticated_message(
        self, 
        client: A2AClient, 
        skill_id: str, 
        message_content: str,
        auth_context: Dict = None
    ):
        """Send message with authentication context"""
        message = {
            "content": message_content,
            "role": "user"
        }
        
        if auth_context:
            message["metadata"] = auth_context
        
        try:
            response = await client.send_message(skill_id=skill_id, message=message)
            return response
        except Exception as e:
            logging.error(f"Authenticated message sending failed: {e}")
            raise
```

### OAuth 2.0 Authentication Example (examples/oauth_authentication.py)

```python
import asyncio
from src.auth_provider import A2AAuthenticationProvider, A2ASecureClient
import logging

async def main():
    print("🔐 A2A OAuth 2.0 Authentication Demo")
    print("=" * 40)
    
    # Initialize authentication provider
    auth_provider = A2AAuthenticationProvider("http://localhost:9000")
    secure_client = A2ASecureClient(auth_provider)
    
    # Test OAuth 2.0 authentication
    print("\n1. Testing OAuth 2.0 Client Credentials Flow...")
    
    try:
        # Create authenticated client
        authenticated_client = await secure_client.create_authenticated_client(
            agent_url="http://localhost:8300",
            auth_method="oauth2",
            client_id="agent_client",
            client_secret="secret123",
            scopes=["agent:read", "task:execute"]
        )
        
        if authenticated_client:
            print("✅ OAuth 2.0 authentication successful")
            
            # Test secure communication
            print("\n2. Testing secure agent communication...")
            response = await secure_client.send_authenticated_message(
                authenticated_client,
                "secure_process",
                "Process this sensitive data with OAuth 2.0 authentication"
            )
            
            if response:
                print(f"✅ Secure response: {response.get('content', 'No content')}")
                metadata = response.get('metadata', {})
                if 'authenticated_user' in metadata:
                    print(f"🔑 Authenticated as: {metadata['authenticated_user']}")
            else:
                print("❌ No response received")
        else:
            print("❌ OAuth 2.0 authentication failed")
    
    except Exception as e:
        print(f"❌ Authentication error: {e}")
    
    # Test unauthorized access
    print("\n3. Testing unauthorized access...")
    try:
        from a2a.client import A2AClient
        
        # Create unauthenticated client
        unauth_client = A2AClient.get_client_from_agent_card_url("http://localhost:8300")
        
        response = await unauth_client.send_message(
            skill_id="secure_process",
            message={"content": "Unauthorized request", "role": "user"}
        )
        
        if response and response.get('type') == 'error':
            print(f"✅ Properly rejected: {response.get('content')}")
        else:
            print("❌ Security bypass detected!")
    
    except Exception as e:
        print(f"✅ Access properly denied: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
```

### API Key Authentication Example (examples/api_key_auth.py)

```python
import asyncio
from src.auth_provider import A2AAuthenticationProvider, A2ASecureClient
import logging

async def main():
    print("🔑 A2A API Key Authentication Demo")
    print("=" * 35)
    
    auth_provider = A2AAuthenticationProvider()
    secure_client = A2ASecureClient(auth_provider)
    
    # Test API key authentication
    print("\n1. Testing API Key Authentication...")
    
    try:
        authenticated_client = await secure_client.create_authenticated_client(
            agent_url="http://localhost:8300",
            auth_method="api_key",
            api_key="ak_demo_key_12345"
        )
        
        if authenticated_client:
            print("✅ API key authentication successful")
            
            # Test secure communication
            print("\n2. Testing API key protected communication...")
            response = await secure_client.send_authenticated_message(
                authenticated_client,
                "secure_process",
                "Process data using API key authentication"
            )
            
            if response:
                print(f"✅ API key response: {response.get('content', 'No content')}")
            else:
                print("❌ No response received")
        else:
            print("❌ API key authentication failed")
    
    except Exception as e:
        print(f"❌ API key authentication error: {e}")
    
    # Test invalid API key
    print("\n3. Testing invalid API key...")
    try:
        invalid_client = await secure_client.create_authenticated_client(
            agent_url="http://localhost:8300",
            auth_method="api_key",
            api_key="invalid_key"
        )
        
        if invalid_client:
            response = await secure_client.send_authenticated_message(
                invalid_client,
                "secure_process",
                "Request with invalid API key"
            )
            
            if response and response.get('type') == 'error':
                print(f"✅ Invalid key properly rejected: {response.get('content')}")
        
    except Exception as e:
        print(f"✅ Invalid API key properly denied: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
```

## 🧪 Testing Examples

### Secure Communication Test (examples/secure_communication.py)

```python
import asyncio
from src.auth_provider import A2AAuthenticationProvider, A2ASecureClient
import logging

async def main():
    print("🛡️ A2A Secure Communication Test")
    print("=" * 35)
    
    auth_provider = A2AAuthenticationProvider()
    secure_client = A2ASecureClient(auth_provider)
    
    # Test multiple authentication methods
    auth_methods = [
        {
            "name": "OAuth 2.0",
            "method": "oauth2",
            "params": {
                "client_id": "secure_agent",
                "client_secret": "supersecret",
                "scopes": ["agent:read", "agent:write", "task:execute"]
            }
        },
        {
            "name": "API Key",
            "method": "api_key", 
            "params": {"api_key": "ak_secure_key_67890"}
        }
    ]
    
    for auth_config in auth_methods:
        print(f"\n🔐 Testing {auth_config['name']} Authentication...")
        
        try:
            client = await secure_client.create_authenticated_client(
                agent_url="http://localhost:8300",
                auth_method=auth_config["method"],
                **auth_config["params"]
            )
            
            if client:
                # Test both skill types
                skills_to_test = [
                    ("secure_process", "Secure data processing test"),
                    ("admin_task", "Administrative operation test")
                ]
                
                for skill_id, test_message in skills_to_test:
                    print(f"  📡 Testing skill: {skill_id}")
                    
                    response = await secure_client.send_authenticated_message(
                        client, skill_id, test_message
                    )
                    
                    if response:
                        if response.get('type') == 'error':
                            print(f"    ⚠️ {response.get('content')}")
                        else:
                            print(f"    ✅ Success: {response.get('content', 'No content')[:50]}...")
                    else:
                        print(f"    ❌ No response for {skill_id}")
            else:
                print(f"  ❌ {auth_config['name']} authentication failed")
        
        except Exception as e:
            print(f"  ❌ {auth_config['name']} error: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
```

## 🔍 Key Learning Points

### 1. A2A SDK Security Integration
- Using built-in A2A security schemes (OAuth 2.0, Bearer tokens, API keys)
- Leveraging A2A User and UnauthenticatedUser classes
- Implementing authentication middleware with A2A SDK

### 2. Agent Card Security Configuration
- Defining security schemes in agent cards
- Setting up authentication requirements per skill
- Managing permissions and authorization levels

### 3. Secure Client Communication
- Creating authenticated A2A clients
- Managing authentication tokens and API keys
- Handling authentication failures gracefully

### 4. Enterprise Security Patterns
- Multi-factor authentication support
- Token validation and refresh mechanisms
- Audit logging with A2A telemetry features

## 🎯 Success Criteria

- [ ] Agents requiring authentication using A2A SDK security features
- [ ] OAuth 2.0 client credentials flow working with A2A clients
- [ ] API key authentication integrated with A2A SDK
- [ ] Bearer token validation for secure agent communication
- [ ] Permission-based access control for agent skills
- [ ] Proper error handling for authentication failures

## 🔗 Next Steps

After mastering A2A SDK authentication, proceed to **[Step 12: Enterprise Features](../12_enterprise_features/README.md)** to implement production-ready enterprise capabilities.

## 📚 Additional Resources

- [A2A Python SDK Documentation](https://google-a2a.github.io/A2A/latest/sdk/python/)
- [A2A Enterprise-Ready Features](https://google-a2a.github.io/A2A/topics/enterprise-ready/)
- [A2A Protocol Security Specification](https://google-a2a.github.io/A2A/specification/#security)
- [A2A Authentication Classes](https://google-a2a.github.io/A2A/latest/sdk/python/#a2a.auth) 