import os
import hmac
import hashlib
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

class WebSocketAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/ws/"):
            api_key = request.headers.get("X-API-Key")
            if not self.verify_key(api_key):
                raise HTTPException(403, "Invalid API key")
        return await call_next(request)
    
    def verify_key(self, key: str) -> bool:
        if not key:  # Handle None or empty key
            return False
        salt = os.getenv("SECRET_SALT", "").encode()  # Fallback to empty string if env var missing
        expected_key = os.getenv("API_KEY", "").encode()  # Fallback to empty string
        expected = hmac.new(salt, expected_key, hashlib.sha256).hexdigest()
        return hmac.compare_digest(
            hmac.new(salt, key.encode(), hashlib.sha256).hexdigest(),
            expected
        )