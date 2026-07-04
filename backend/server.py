"""ASGI entrypoint for the supervisor-managed uvicorn process.

Supervisor runs `uvicorn server:app` from /app/backend. This exposes the
Django ASGI application as `app` so the Django+DRF backend is served on :8001.
"""
from config.asgi import application as app

__all__ = ["app"]
