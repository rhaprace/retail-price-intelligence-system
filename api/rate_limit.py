import os
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi import FastAPI, Request

DEFAULT_RATE_LIMIT = os.getenv("API_RATE_LIMIT", "100/minute")
AUTH_RATE_LIMIT = os.getenv("AUTH_RATE_LIMIT", "10/minute")
HEAVY_RATE_LIMIT = os.getenv("HEAVY_RATE_LIMIT", "20/minute")


def get_identifier(request: Request) -> str:
    if hasattr(request.state, 'user') and request.state.user:
        return f"user:{request.state.user.id}"
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return f"apikey:{api_key}"
    
    return get_remote_address(request)


limiter = Limiter(key_func=get_identifier)


def setup_rate_limiting(app: FastAPI):
    app.state.limiter = limiter
    
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    app.add_middleware(SlowAPIMiddleware)


def default_limit():
    return limiter.limit(DEFAULT_RATE_LIMIT)


def auth_limit():
    return limiter.limit(AUTH_RATE_LIMIT)


def heavy_limit():
    return limiter.limit(HEAVY_RATE_LIMIT)


def custom_limit(limit_string: str):
    return limiter.limit(limit_string)
