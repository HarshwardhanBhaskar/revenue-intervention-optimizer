"""
Rate Limiting Middleware — In-Memory Sliding Window Rate Limiter.

Protects against:
- DoS & API Flooding attacks
- Credential stuffing / brute force
- Webhook spamming
"""

import time
from collections import defaultdict
from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 120, max_content_length: int = 1_048_576):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.max_content_length = max_content_length # 1MB limit against memory exhaustion DoS
        self.request_history: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        # 1. Payload Size DoS Protection
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_content_length:
            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content={"error": "Payload size exceeds maximum allowed limit (1MB)"},
            )

        # 2. Extract Client Identifier (IP or Forwarded IP)
        client_ip = request.headers.get("x-forwarded-for") or (request.client.host if request.client else "unknown")
        current_time = time.time()
        window_start = current_time - 60.0

        # Prune old request timestamps
        history = self.request_history[client_ip]
        self.request_history[client_ip] = [t for t in history if t > window_start]

        # 3. Check Rate Limit Exceeded
        if len(self.request_history[client_ip]) >= self.requests_per_minute:
            retry_after = int(60.0 - (current_time - self.request_history[client_ip][0]))
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded. Please try again later.",
                    "limit_per_minute": self.requests_per_minute,
                    "retry_after_seconds": max(1, retry_after),
                },
                headers={"Retry-After": str(max(1, retry_after))},
            )

        self.request_history[client_ip].append(current_time)

        # Process Request
        response: Response = await call_next(request)
        return response
