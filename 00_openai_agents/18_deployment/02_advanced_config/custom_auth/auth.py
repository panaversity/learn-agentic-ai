from typing import Dict, Optional, Any
import os
from datetime import datetime, timedelta
import jwt
from dotenv import load_dotenv

load_dotenv()

class AuthConfig:
    """Authentication configuration and utilities"""
    
    def __init__(self):
        self.secret_key = os.getenv("AUTH_SECRET", "your-secret-key")
        self.token_expiry = timedelta(hours=24)
        self.oauth = {
            "google": {
                "client_id": os.getenv("GOOGLE_OAUTH_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")
            },
            "github": {
                "client_id": os.getenv("GITHUB_OAUTH_CLIENT_ID"),
                "client_secret": os.getenv("GITHUB_OAUTH_CLIENT_SECRET")
            }
        }

    def create_token(self, user_data: Dict[str, Any]) -> str:
        """Create JWT token for authenticated user"""
        payload = {
            "user_id": user_data.get("id"),
            "email": user_data.get("email"),
            "exp": datetime.utcnow() + self.token_expiry
        }
        return jwt.encode(payload, self.secret_key, algorithm="HS256")

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            return jwt.decode(token, self.secret_key, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def get_oauth_config(self, provider: str) -> Optional[Dict[str, str]]:
        """Get OAuth configuration for specified provider"""
        return self.oauth.get(provider)

# Authentication middleware for Chainlit
async def auth_middleware():
    """
    Chainlit authentication middleware
    
    Returns:
        Dict containing user information if authenticated
    """
    auth_config = AuthConfig()
    
    # Example of custom authentication logic
    async def custom_auth(request):
        token = request.headers.get("Authorization")
        if not token:
            return None
            
        # Remove 'Bearer ' prefix if present
        token = token.replace("Bearer ", "")
        return auth_config.verify_token(token)
    
    return {
        "auth_type": "custom",
        "auth_function": custom_auth,
        "providers": list(auth_config.oauth.keys())
    }

# Example usage in chainlit.md
"""
# Welcome to Authenticated Chat! 👋

Please log in to continue:

- Google Sign In
- GitHub Sign In

Your session will be valid for 24 hours.
""" 
async def main():
    auth_config = await auth_middleware()
    print(auth_config)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
