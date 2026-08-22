"""
Security Headers Middleware — Enforces OWASP-recommended HTTP security headers.

Protects against:
- Clickjacking (X-Frame-Options)
- MIME-type sniffing (X-Content-Type-Options)
- XSS / Script injection
- Data leakage (Referrer-Policy)
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        
        # Add OWASP hardened security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=()"
        
        return response
