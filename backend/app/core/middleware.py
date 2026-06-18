from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class SimpleRateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 120):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.hits: dict[str, deque[datetime]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else 'unknown'
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(minutes=1)

        queue = self.hits[client_ip]
        while queue and queue[0] < window_start:
            queue.popleft()

        if len(queue) >= self.requests_per_minute:
            return JSONResponse({'detail': 'Rate limit exceeded'}, status_code=429)

        queue.append(now)
        return await call_next(request)
